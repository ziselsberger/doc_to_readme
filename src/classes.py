from typing import Tuple

import yaml


class TechnicalQualityTests:
    """Base class for all technical QC Tests."""

    def __init__(
            self,
            config_file: str
    ):
        """
        Initiate class TechnicalQualityTests.

        Args:
            config_file (str): Path to config file (YAML).

        Raises:
            SystemExit: No configuration file provided.
        """
        if not config_file:
            raise SystemExit("No configuration file provided.")
        with open(config_file, "r", encoding="utf-8") as file:
            self.config = yaml.load(file, Loader=yaml.FullLoader)

        self.qc_report_dict = {}

    def add_to_dict(
            self,
            test_name: str,
            test_result: Tuple[bool, str]
    ) -> None:
        """Add QC result to dictionary.

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
