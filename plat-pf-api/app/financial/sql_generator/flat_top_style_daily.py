from datetime import timedelta

from app.financial.sql_generator.flat_top_style_base import FlatTopPerformingStylesBaseSQLGenerator


class FlatTopPerformingStylesDailySQLGenerator(FlatTopPerformingStylesBaseSQLGenerator):
    """
    SQL Generator for Flat Top Performing Styles on a Daily Basis.
    """

    def get_current_date_calculated(self):
        """
        Returns the date range for the most recent complete day (yesterday).
        """
        return (
            self.yesterday.strftime("%Y-%m-%d 00:00:00"),
            self.yesterday.strftime("%Y-%m-%d 23:59:59")
        )

    def get_previous_date_calculated(self):
        """
        Returns the date range for the day before yesterday.
        """
        prior_yesterday = self.yesterday - timedelta(days=1)
        return (
            prior_yesterday.strftime("%Y-%m-%d 00:00:00"),
            prior_yesterday.strftime("%Y-%m-%d 23:59:59")
        )
