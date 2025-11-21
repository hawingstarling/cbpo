from datetime import timedelta

from app.financial.sql_generator.flat_top_style_base import FlatTopPerformingStylesBaseSQLGenerator


class FlatTopPerformingStyles30DaysSQLGenerator(FlatTopPerformingStylesBaseSQLGenerator):
    """
        SQL Generator for Flat Top Performing Styles on a 30Days Basis.
        """

    def get_current_date_calculated(self):
        """
        Returns the date range for the most recent complete day (yesterday).
        """
        prior_30d = self.yesterday - timedelta(days=30)
        return (
            prior_30d.strftime("%Y-%m-%d 00:00:00"),
            self.yesterday.strftime("%Y-%m-%d 23:59:59")
        )

    def get_previous_date_calculated(self):
        """
        Returns the date range for the day before yesterday.
        """
        year = self.yesterday.year - 1
        prior_30d = self.yesterday - timedelta(days=30)
        prior_30d = prior_30d.replace(year=year)
        prior_yesterday = self.yesterday.replace(year=year)
        return (
            prior_30d.strftime("%Y-%m-%d 00:00:00"),
            prior_yesterday.strftime("%Y-%m-%d 23:59:59")
        )
