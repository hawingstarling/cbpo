const thirtyDaySales = require('./30DaySales.json')
const thirtyDaySales$ = require('./30DaySales($).json')
const thirtyDaySales$Brand = require('./30DaySales($)Brand.json')
const AERepricingInstance = require('./AERepricingInstance.json')
const AgedInventoryLine = require('./AgedInventoryLine')
const AgedInventoryTable = require('./AgedInventoryTable')
const AllOrdersDay = require('./AllOrdersDay')
const AllOrdersMonth = require('./AllOrdersMonth')
const AllSales = require('./AllSales')
const AllSalesComparison = require('./AllSalesComparison')
const AverageSalesPrice = require('./AverageSalesPrice')
const BigMovesDown = require('./BigMovesDown')
const BigMovesUp = require('./BigMovesUp')
const ETBigMovesDown = require('./E&TBigMovesDown')
const ETBigMovesUP = require('./E&TBigMovesUP')
const ETGraph = require('./E&TGraph')
const HandlingTime = require('./HandlingTime')
const INVCustomerReturnsBrand = require('./INVCustomerReturnsBrand')
const INVCustomerReturnsCategory = require('./INVCustomerReturnsCategory')
const InventoryValues = require('./InventoryValues')
// const KeyMetrics30Days = require('./KeyMetrics30Days')
const MFNCategoryDate = require('./MFNCategoryDate')
const MFNCategorySegment = require('./MFNCategorySegment')
const MoHValues = require('./MoHValues')
const MovementTodayvLastYearDown = require('./MovementTodayvLastYearDown')
const MovementTodayvLastYearUp = require('./MovementTodayvLastYearUp')
const OrderedProductSales30days = require('./OrderedProductSales30days')
const OrderedProductSalesToday = require('./OrderedProductSalesToday')
const OverviewSale = require('./OverviewSale')
const Salesby$Amount = require('./Salesby$Amount')
const StoreOnlineSales = require('./StoreOnlineSales')
const TotalInventory = require('./TotalInventory')
const TotalRAOrder30Days = require('./TotalRAOrder30Days')
const YOYMonthlySales = require('./YOYMonthlySales')
const AverageSalesPriceYesterday = require('./AverageSalesPriceYesterday')
const TotalSalesTracker = require('./TotalSalesTracker')
const PAndL = require('./PAndL.json')
const TopProductPerformance = require('./TopProductPerformance.json')
const BrokenDownSales = require('./BrokenDownSales.json')
const SalesByASIN = require('./SalesByASIN.json')
const OverallSales = require('./OverallSales.json')
const SalesByDivision = require('./SalesByDivision.json')
const TopPerformingStylesBySegment = require('./TopPerformingStylesBySegment.json')

let OverviewSaleFirst = OverviewSale[0]
let OverviewSaleSecond = OverviewSale[1]
let OverviewSaleThird = OverviewSale[2]

let dashboardWidget = {
  thirtyDaySales,
  thirtyDaySales$,
  thirtyDaySales$Brand,
  AERepricingInstance,
  AgedInventoryLine,
  AgedInventoryTable,
  AllOrdersDay,
  AllOrdersMonth,
  AllSales,
  AllSalesComparison,
  AverageSalesPrice,
  BigMovesDown,
  BigMovesUp,
  ETBigMovesDown,
  ETBigMovesUP,
  ETGraph,
  HandlingTime,
  INVCustomerReturnsBrand,
  INVCustomerReturnsCategory,
  InventoryValues,
  // KeyMetrics30Days,
  MFNCategoryDate,
  MFNCategorySegment,
  MoHValues,
  MovementTodayvLastYearDown,
  MovementTodayvLastYearUp,
  OrderedProductSales30days,
  OrderedProductSalesToday,
  OverviewSaleFirst,
  OverviewSaleSecond,
  OverviewSaleThird,
  Salesby$Amount,
  StoreOnlineSales,
  TotalInventory,
  TotalRAOrder30Days,
  YOYMonthlySales,
  AverageSalesPriceYesterday,
  TotalSalesTracker,
  PAndL,
  TopProductPerformance,
  BrokenDownSales,
  SalesByASIN,
  OverallSales,
  SalesByDivision,
  TopPerformingStylesBySegment
}

export default dashboardWidget
