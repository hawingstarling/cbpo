import calendar

from dateutil.relativedelta import relativedelta

from app.financial.sql_generator.flat_top_style_base import FlatTopPerformingStylesBaseSQLGenerator


class FlatTopPerformingStylesMTDSQLGenerator(FlatTopPerformingStylesBaseSQLGenerator):
    """
    SQL Generator for Flat Top Performing Styles on a MTD Basis.
    """

    def get_current_date_calculated(self):
        """
        Returns the date range for the most recent complete day (yesterday).
        """
        return (
            self.yesterday.strftime("%Y-%m-01 00:00:00"),
            self.yesterday.strftime("%Y-%m-%d 23:59:59")
        )

    def get_previous_date_calculated(self):
        """
        Returns the date range for the day before yesterday.
        """
        prior_month = self.yesterday - relativedelta(months=1)
        number_day = calendar.monthrange(self.yesterday.year, prior_month.month)[1]
        if self.yesterday.day > number_day:
            prior_month.day = number_day
        return (
            prior_month.strftime("%Y-%m-01 00:00:00"),
            prior_month.strftime("%Y-%m-%d 23:59:59")
        )
