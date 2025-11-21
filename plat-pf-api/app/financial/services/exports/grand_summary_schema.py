import pandas as pd
from django.db.models import QuerySet
from typing import Union
from app.financial.services.exports.schema import ExportSchema


class GrandSummaryExportSchema(ExportSchema):
    def __init__(self, client_id: str, columns: dict, queryset: Union[QuerySet, None, str], category: str, **kwargs):
        super().__init__(client_id, columns, queryset, category, **kwargs)
        self._df_aggregate: bool = True

    @property
    def df_aggregate(self):
        return self._df_aggregate

    @df_aggregate.setter
    def df_aggregate(self, val: bool):
        self._df_aggregate = val

    def _load_data_frame(self, data: any):
        df = super()._load_data_frame(data)
        if self.df_aggregate:
            df = pd.concat([df, df.sum(numeric_only=True).to_frame().T], ignore_index=True)
            df.loc[df.index[-1], 'Brand'] = 'Grand Total'
            df.loc[df.index[-1], 'Margin'] = None
        df['Total Sales'] = df['Total Sales'].round(2).astype(float).map('{:,}'.format)
        df['COGS'] = df['COGS'].round(2).astype(float).map('{:,}'.format)
        df['Actual Shipping Cost'] = df['Actual Shipping Cost'].round(2).astype(float).map('{:,}'.format)
        df['Estimated Shipping Cost'] = df['Estimated Shipping Cost'].round(2).astype(float).map('{:,}'.format)
        df['Profit'] = df['Profit'].round(2).astype(float).map('{:,}'.format)
        df['Margin'] = df['Margin'].astype(float).map('{:.2%}'.format, na_action='ignore').fillna("-")
        return df.style.set_properties(**{"text-align": "center"}, subset=[
            "Total Sales",
            "COGS",
            "Actual Shipping Cost",
            "Estimated Shipping Cost",
            "Profit",
            "Margin"
        ]).set_properties(**{"background-color": "#2ECC71", "font-weight": "bold"}, subset=df.index[-1])
