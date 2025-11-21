from app.financial.sql_generator.flat_top_style_base import FlatTopPerformingStylesBaseSQLGenerator


class FlatTopPerformingStylesYTDSQLGenerator(FlatTopPerformingStylesBaseSQLGenerator):
    """
    SQL Generator for Flat Top Performing Styles on a YTD Basis.
    """

    def get_current_date_calculated(self):
        """
        Returns the date range for the most recent complete day (yesterday).
        """
        return (
            self.yesterday.strftime("%Y-01-01 00:00:00"),
            self.yesterday.strftime("%Y-%m-%d 23:59:59")
        )

    def get_previous_date_calculated(self):
        """
        Returns the date range for the day before yesterday.
        """
        year = self.yesterday.year - 1
        prior_year = self.yesterday.replace(year=year)
        return (
            prior_year.strftime("%Y-01-01 00:00:00"),
            prior_year.strftime("%Y-%m-%d 23:59:59")
        )
