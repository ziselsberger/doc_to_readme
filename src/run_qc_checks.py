# pylint: disable=[C0413, W0511, C0116, C0115]
# C0413: wrong-import-position
# W0511: TODO?
# C0116: Missing function or method docstring (missing-function-docstring)
# C0115: Missing class docstring (missing-class-docstring)

"""Module containing functions and classes used for execution of QC Checks"""
#
# import argparse
# import json
# import os
# import sys
# from datetime import datetime
# from typing import Callable, Union, Any, Optional, Tuple
#
# import geopandas
# import pandas
# import rasterio
# import yaml
#
# SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
# sys.path.append(os.path.dirname(SCRIPT_DIR))
#
# import run_qc.aux_functions.s3_functions as s3f
# import qc_raster.aggregation as agg
# from qc_general import crs, extent, filename, attributes_and_values, \
#     ancillary_files
# from qc_raster import border, colormap, raster_properties
# from qc_raster.raster_properties import get_reader, get_profile
# from qc_report import markdown as md
# from qc_vector import vector_properties as vp

RasterProfile = rasterio.profiles.Profile
DatasetReader = rasterio.io.DatasetReader


class TechnicalQualityTests:
    """
    Base class for all technical QC Tests.

    Results will be either written to a JSON file or to HTML report.
    If one or more tests fail, TechnicalQualityTests will return an Error Code.
    Otherwise, the input dataset will be written to a specified output folder / S3 Bucket.
    """

    def __init__(
            self,
            config_file: str,
            test_input: str
    ):
        """
        Initiate class TechnicalQualityTests.

        Args:
            config_file (str): Path to config file (YAML).
            test_input (str): Path to file, which shall be checked.

        Raises:
            SystemExit: No configuration file provided.
            SystemExit: No test dataset provided.
        """
        if not config_file:
            raise SystemExit("No configuration file provided.")
        with open(config_file, "r", encoding="utf-8") as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)

        if not test_input:
            raise SystemExit("No test dataset provided.")

        self.test_input = test_input
        self.tests = None
        self.ref_file = self.config.get("reference_file", '')
        self.qc_report_dict = {}  # dict for all qc results
        self.tile_id = test_input.split("_")[-3]

        # s3 client for reading and writing files to s3 bucket
        try:
            self.s3_client = s3f.start_s3_client()
        except:
            self.s3_client = None
        s3f.s3_client = self.s3_client

    @property
    def reference_file(self) -> str:
        """
        Updates path to reference file, in case placeholders are used, 
        which need to be replace for every file, that shall be checked.
        e.g. when the filename includes a Tile ID.

        Returns:
            str: Updated path to reference file.
        """
        return self.ref_file

    def add_to_dict(
            self,
            test_name: str,
            test_result: Tuple[bool, str]
    ) -> None:
        """
        Add QC result to dictionary.

        Args:
            test_name (str): Name of QC check
            test_result (Tuple[bool, str]): Result of QC check
        """
        try:
            self.qc_report_dict[test_name] = test_result
        except TypeError:
            self.qc_report_dict[test_name] = (
                False,
                f"Not completed."
            )

    def execute_test(
            self,
            test_name: str,
            func: Callable[..., Any],
            inp: Union[str, RasterProfile, DatasetReader],
            specification: Optional[Any] = '',
            header: Optional[str] = '',
            **kwargs
    ) -> None:
        """
        Run QC function and write results in a dictionary.

        Args:
            test_name (str): Name of QC check
            func (Callable[..., Any]): QC function
            inp (Union[str, RasterProfile, DatasetReader]): Input for QC
                (path to file)
            specification (Optional[Any], optional): Specification extracted
                from config file. Defaults to ''.
            header (Optional[str], optional): Header for test result in
                QC Report. Defaults to ''.
        """
        if test_name in self.tests:
            if not specification:
                specification = self.tests[test_name]
                if specification is None:
                    return

            # TODO: check if all checks return None in case of failure or a valid test_result
            test_result = func(inp, specification, **kwargs)

            TechnicalQualityTests.add_to_dict(
                self,
                test_name=header if header is not None else test_name,
                test_result=test_result
            )

    def run_qc(self):
        """
        Run QC checks
        """

        # Load list of tests from config file and remove those,
        # where no specification has been added.
        tests = self.config.get('Tests')
        self.tests = {test: spec for test, spec in tests.items()
                      if tests.get(test)}

        # ========================= QC CHECKS =================================
        try:
            report = self.test_input.replace(
                os.path.splitext(self.test_input)[1],
                ".html" if self.config.get("html_report") else ".json"
            )
            if not os.path.exists(report) or self.config.get("overwrite"):
                TechnicalQualityTests.tests(self)
        except Exception as e:
            print(e)
        finally:
            results = TechnicalQualityTests.finalise_qc(self)

        return results

    def finalise_qc(self) -> dict:
        """
        Finalise QC checks.

        - Write results to JSON
        - All tests passed: save file to S3 Bucket

        Raises:
            SystemExit - in case of one or more failed tests

        """

        json_dict = {
            test: {
                "Test Result": result[1].split("\n")[0].strip("."),
                "Specifications": result[1].split("\n")[1].strip("Specifications: ").replace("'", ""),
                "Tested file": result[1].split("\n")[2].strip("Tested file: ").replace("'", ""),
                "Info": result[1].split("\n")[4:] if len(result[1].split("\n")) > 3 else None
            }
            for test, result in self.qc_report_dict.items()
        }

        if self.config.get("html_report"):
            md_file = f"{os.path.splitext(self.test_input)[0]}.html"
            if os.path.exists(md_file):
                if self.config.get("overwrite"):
                    os.remove(md_file)
                else:
                    print(f"QC Report already exists: {md_file}")
                    return json_dict
            md.md_start_qc(
                in_file=self.test_input,
                qb=self.config.get("qb"),
                md_file=md_file
            )
            for test, result in self.qc_report_dict.items():
                md.md_test_result(
                    test_name=test,
                    result=result,
                    file=md_file
                )
            md.md_results_summary(
                file=md_file,
                **self.qc_report_dict)
        else:
            # add all test results to JSON File
            json_logfile = f"{os.path.splitext(self.test_input)[0]}.json"
            with open(json_logfile, "w") as outfile:
                json.dump(json_dict, outfile, indent=4)

        results_df = pandas.DataFrame.from_dict(
            self.qc_report_dict,
            orient="index",
            columns=["Passed", "Message"]
        )

        total_tests = len(results_df)
        passed_tests = len(results_df[results_df["Passed"] == True])
        if passed_tests == total_tests:
            print(f"QC finished successfully. "
                  f"Passed: {passed_tests} of {total_tests} tests.")
            # TODO: write data to S3 Bucket
            # print("Write file to trusted zone...")
        else:
            print(f"Tests failed: {total_tests - passed_tests}, "
                  f"passed: {passed_tests} of {total_tests} tests.")
            # raise SystemExit(1)  # QC Error Code
        return json_dict

    def tests(self) -> None:
        """
        Includes all QC checks (independent of data format).
        Only those checks are executed, where a specification could be
        extracted from the config file.
        """

        # Coordinate Reference System
        spec_crs = self.tests.get('crs')
        if isinstance(spec_crs, (str, bool)):
            spec_crs = self.reference_file
        TechnicalQualityTests.execute_test(
            self,
            test_name='crs',
            func=crs.check_crs,
            inp=self.test_input,
            header="Coordinate reference system",
            specification=spec_crs
        )

        # Attributes
        if "attributes" in self.tests:
            attributes = [a.strip() for a in self.tests['attributes'].split(",")] \
                if isinstance(self.tests['attributes'], str) \
                else self.tests['attributes']

            if isinstance(attributes, list):
                ras_attr = f"{os.path.splitext(self.test_input)[0]}.tif.vat.dbf"  # raster attribute table
                input = ras_attr if os.path.exists(
                    ras_attr) else self.test_input  # (s3f.get_file_from_s3(ras_attr) is not None
                # or os.path.exists(ras_attr)) \
                # else self.test_input

                TechnicalQualityTests.execute_test(
                    self,
                    test_name='attributes',
                    func=attributes_and_values.check_attribute_table,
                    inp=input,
                    specification=attributes,
                    header="Attributes"
                )
            # else:  # TODO: refactor
            #     self.log.error(f"Attributes not provided as string or list.")

        # Value Range
        if "valid_value_range" in self.tests:
            value_field = self.tests.get("value_field", 'Value')
            value_range = self.tests.get("valid_value_range")

            ras_attr = f"{os.path.splitext(self.test_input)[0]}.tif.vat.dbf"  # raster attribute table
            attribute_file = ras_attr if os.path.exists(ras_attr) else self.test_input

            TechnicalQualityTests.execute_test(
                self,
                test_name="valid_value_range",
                func=attributes_and_values.check_value_range,
                inp=attribute_file,
                specification=value_range,
                value_field=value_field,
                header="Value Range"
            )

        # Extent
        if 'extent' in self.tests:
            # spec_extent = None
            # bvl = r"t:\processing\2771_VLCC_EEA\02_Interim_Products\BVL\BVL_20221014\20221014\30SVH\CLMS_HRLVLCC_BVL_all_years_10m_30SVH_3035_V010.tif"
            # self.ref_file = bvl.replace("30SVH", self.tile_id)
            if isinstance(self.tests.get('extent'), (list, tuple)):
                spec_extent = self.tests.get('extent')
            elif self.reference_file is not None:
                spec_extent = self.ref_file
            # else:  # TODO: refactor
            #     log_message(self.log.warning, "Reference file / BBox was not specified or not found!")

            if spec_extent:
                TechnicalQualityTests.execute_test(
                    self,
                    test_name='extent',
                    func=extent.check_extent,
                    inp=self.test_input,
                    specification=spec_extent,
                    header="Extent"
                )

        # Filename
        if "filename_specs" in self.tests:
            TechnicalQualityTests.execute_test(
                self,
                test_name='filename_specs',
                func=filename.check_filename,
                inp=self.test_input,
                specification=self.tests['extension'],
                header="Filename",
                specifications=self.tests['filename_specs']
            )

        # Tabular data
        if "table" in self.tests:
            test_table = attributes_and_values.check_table(
                in_file=self.test_input,
                specifications=self.tests['table']
            )
            # TODO: add to results dict :-)
            # TechnicalQualityTests.add_to_dict(
            #     self,
            #     test_name='validity',
            #     test_result=test_validity
            # )

        # Ancillary Files
        aux_files = self.tests.get('aux_files', {})

        for ancillary_file, specification in aux_files.items():
            find_file = ancillary_files.look_for_file(
                descriptive_name=ancillary_file,
                filename=specification.get('filename', self.test_input),
                specified_extension=specification.get('ext'),
                folder=specification.get('folder')
            )
            TechnicalQualityTests.add_to_dict(
                self,
                test_name=ancillary_file,
                test_result=find_file
            )

        # Aggregation
        if ('aggregation_raster' or 'aggregation_from_vector') in self.tests:
            agg_config = self.tests.get('aggregation_raster',
                                        self.tests.get('aggregation_from_vector'))
            agg_check = agg_config.get('agg_check', 'binary')
            input_file = agg_config.get('input_file', '')
            agg_function = agg_config.get('agg_function', 'mean')
            exclude_all_nodata = agg_config.get('exclude_all_nodata', True)
            num_samples = agg_config.get('num_samples', 10)
            nodata_value = agg_config.get('nodata_value')

            # predefined result
            class_result = (False, "Failed. Some error occurred while processing. "
                                   "Please check LogFile.")

            if 'aggregation_raster' in self.tests:
                if agg_check == "binary":
                    class_result = agg.check_aggregation_raster_class(
                        input_data=input_file,
                        out_ras_file=self.test_input,
                        nodata=nodata_value,
                        samples=num_samples,
                        raster_class=agg_config.get('raster_class'),
                        aggregation_function=agg_function,
                        exclude_all_0=exclude_all_nodata,
                        return_dict=False
                    )
                elif agg_check == "cont":
                    class_result = agg.check_aggregation_continuous_raster(
                        input_data=input_file,
                        out_ras_file=self.test_input,
                        nodata=nodata_value,
                        raster_class=None,
                        exclude_all_0=exclude_all_nodata,
                        return_dict=False
                    )
                elif agg_check == "border":
                    filter_type = agg_config.get('filter_type', 'prewitt')
                    class_result = agg.check_aggregation_boundary(
                        input_data=input_file,
                        out_ras_file=self.test_input,
                        nodata=None,
                        exclude_all_0=True,
                        raster_class=agg_config.get('raster_class'),
                        filter_type=filter_type,
                        return_dict=False
                    )
                elif agg_check == "nodata":
                    uq_agg_val = agg_config.get('unique_aggregated_value')
                    class_result = agg.check_aggregation_254(
                        input_data=input_file,
                        out_ras_file=self.test_input,
                        nodata=nodata_value,
                        samples=num_samples,
                        exclude_all_0=False,
                        unique_aggregated_value=uq_agg_val)

            elif 'aggregation_from_vector' in self.tests:
                layer = agg_config.get('layer')
                attribute_name = agg_config.get('attribute_name')
                attribute_class = agg_config.get('attribute_class')
                extract_area = agg_config.get('extract_area', True)
                bbox = agg_config.get('bbox')
                input_resolution = agg_config.get('input_res', 10)

                vector = geopandas.read_file(
                    filename=input_file,
                    layer=layer,
                    bbox=bbox
                )

                selection = vector[attribute_name] == attribute_class
                if len(vector[selection]) == 0:
                    selection = vector[attribute_name] == str(attribute_class)
                sel_class_polygons = vector[selection]

                if len(sel_class_polygons) == 0:
                    print("No intersecting polygons found.")

                # set_crs
                ras_crs = rasterio.open(self.test_input).crs
                if vector.crs != ras_crs:
                    sel_class_polygons = sel_class_polygons.to_crs(ras_crs)

                class_result = agg.check_aggregation_vector(
                    input_data=sel_class_polygons,
                    out_ras_file=self.test_input,
                    samples=num_samples,
                    nodata=nodata_value,
                    raster_class=None,
                    exclude_all_0=exclude_all_nodata,
                    input_resolution=input_resolution,
                    extract_area=extract_area,
                    return_dict=False
                )

            TechnicalQualityTests.add_to_dict(
                self,
                test_name="Aggregation",
                test_result=class_result
            )

        # ---------------------------------------------------------------------
        # VECTOR CHECKS
        # ---------------------------------------------------------------------

        # Driver
        TechnicalQualityTests.execute_test(
            self,
            test_name='vector_driver',
            func=vp.check_driver,
            inp=self.test_input,
            header="Driver"
        )

        # File not empty
        if self.tests.get('validity'):
            test_validity = vp.check_vector_file_content(
                vector_file=self.test_input
            )
            TechnicalQualityTests.add_to_dict(
                self,
                test_name='validity',
                test_result=test_validity
            )

        # Minimum mapping unit (m2)
        TechnicalQualityTests.execute_test(
            self,
            test_name='vector_mmu',
            func=vp.check_mmu,
            inp=self.test_input,
            header="Minimum mapping unit"
        )

        # ---------------------------------------------------------------------
        # RASTER CHECKS
        # ---------------------------------------------------------------------
        try:
            # Raster Profile
            profile = get_profile(file=self.test_input)
            # DatasetReader
            reader = get_reader(file=self.test_input)
        except AttributeError as att_err:
            print(att_err)
            pass
        else:
            # Data Type
            TechnicalQualityTests.execute_test(
                self,
                test_name='data_type',
                func=raster_properties.check_data_type,
                inp=reader,
                header="Data Type"
            )

            # Driver
            TechnicalQualityTests.execute_test(
                self,
                test_name='raster_driver',
                func=raster_properties.check_driver,
                inp=profile,
                header="Driver"
            )

            # Spatial Resolution
            TechnicalQualityTests.execute_test(
                self,
                test_name='resolution',
                func=raster_properties.check_spatial_resolution,
                inp=reader,
                header="Resolution"
            )

            # NoData Value
            TechnicalQualityTests.execute_test(
                self,
                test_name='nodata',
                func=raster_properties.check_no_data_value,
                inp=reader,
                header="NoData"
            )

            # File compression
            TechnicalQualityTests.execute_test(
                self,
                test_name='compression',
                func=raster_properties.check_compression,
                inp=profile,
                header="Compression"
            )

            # Block size
            TechnicalQualityTests.execute_test(
                self,
                test_name='blocksize',
                func=raster_properties.check_blocksize,
                inp=profile,
                header="Blocksize"
            )

            # Number of raster bands
            TechnicalQualityTests.execute_test(
                self,
                test_name='bands',
                func=raster_properties.check_bands,
                inp=profile,
                header="Number of bands"
            )

        # Overviews / Pyramiden
        TechnicalQualityTests.execute_test(
            self,
            test_name='overviews',
            func=raster_properties.check_overviews,
            inp=self.test_input,
            header="Pyramids"
        )

        # Minimum mapping unit (pixel)
        # TODO: add parameter for direction!
        if "GRAC" in self.test_input:
            TechnicalQualityTests.execute_test(
                self,
                test_name='raster_mmu',
                func=raster_properties.check_mmu_vlcc_grac,
                inp=self.test_input,
                header="Minimum mapping unit"
            )
        else:
            TechnicalQualityTests.execute_test(
                self,
                test_name='raster_mmu',
                func=raster_properties.check_mmu,
                inp=self.test_input,
                header="Minimum mapping unit"
            )

        # # BVL mask
        # if self.tests.get("mask_layer"):
        #     bvl = r"t:\processing\2771_VLCC_EEA\02_Interim_Products\BVL\BVL_20221014\20221014\30SVH\CLMS_HRLVLCC_BVL_all_years_10m_30SVH_3035_V010.tif"
        #     self.ref_file = bvl.replace("30SVH", self.tile_id)
        #     if self.ref_file is not None:
        #         valid_border = self.tests["valid_border"]
        #         correct_border = border.check_mask_vlcc(
        #             self.test_input,
        #             boundary_file=self.ref_file,
        #             inside_value=valid_border.get('inside_value')
        #         )
        #         TechnicalQualityTests.add_to_dict(
        #             self,
        #             test_name="BVL_mask",
        #             test_result=correct_border
        #         )

        # Border
        if self.tests.get("valid_border"):
            if self.ref_file is not None:
                valid_border = self.tests["valid_border"]
                mask = valid_border.get('mask', False)
                correct_border = border.check_border(
                    self.test_input,
                    boundary_file=self.ref_file,
                    inside_value=valid_border.get('inside_value'),
                    no_data_value=valid_border.get('no_data_value'),
                    valid_outside=valid_border.get('valid_outside'),
                    mask=mask
                )
                TechnicalQualityTests.add_to_dict(
                    self,
                    test_name="valid_border" if not mask else "valid_mask",
                    test_result=correct_border
                )

        # Colormap
        TechnicalQualityTests.execute_test(
            self,
            test_name='colormap_embedded',
            func=colormap.check_colormap,
            inp=self.test_input,
            header="Colormap embedded"
        )
        TechnicalQualityTests.execute_test(
            self,
            test_name='colormap_correct',
            func=colormap.compare_colormaps,
            inp=self.test_input,
            header="Colormap values"
        )

        # COG
        if self.tests.get("cog"):
            valid_cog = raster_properties.check_cog(
                raster=self.test_input
            )
            TechnicalQualityTests.add_to_dict(
                self,
                test_name="valid_COG",
                test_result=valid_cog
            )

        # Change
        # TODO: create test

        # Thematic consistency
        # TODO: create test

        # Geometric consistency
        # TODO: create test


def main(config_file=None, test_input=None):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-c",
        "--config",
        help="Path to config file.",
        required=True if test_input is None else False
    )
    parser.add_argument(
        "-i",
        "--test_input",
        help="Path to input dataset",
        required=True if test_input is None else False
    )
    parser.add_argument(
        "--check_only",
        help="Checked files won't be copied to another location after a passed test",
        default=False,
        required=False
    )
    args = parser.parse_args()

    if test_input is None: test_input = args.test_input
    if config_file is None: config_file = args.config

    if test_input.endswith((".txt", ".csv")):
        files = pandas.read_table(
            test_input,
            header=None,
            dtype="str")[0].to_list()
    else:
        files = [test_input]

    all_results = {}
    for file in files:
        try:
            qc_results = TechnicalQualityTests(config_file, file).run_qc()
        except Exception as e:
            print(e)
        else:
            results_df = pandas.DataFrame.from_dict(
                qc_results,
                orient="index",
                columns=["Test Result", "Specification", "Tested File", "Info"]
            )
            all_results[file] = results_df['Test Result'].to_dict()

    if len(files) > 1:
        all_results_df = pandas.DataFrame.from_dict(
            all_results,
            orient="index"
        )
        csv_file = f"_QC_summary_{datetime.today().strftime('%b-%d-%Y_%H-%M')}.csv"
        all_results_df.to_csv(test_input.replace('.txt', csv_file), sep=";")
        # all_results_df.to_csv(f"{os.path.dirname(test_input)}"
        #                       f"/QC_summary_{datetime.today().strftime('%b-%d-%Y_%H-%M')}.csv", sep=";")


if __name__ == "__main__":
    main()
