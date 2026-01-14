export const DEFAULT_NUMERIC_FORMAT = {
  comma: true,
  precision: 2,
  /**
   * NOTE! This will override the precision.
   * @see https://en.wikipedia.org/wiki/Metric_prefix#List_of_SI_prefixes
   */
  siPrefix: false,
  abs: false
}

export const DEFAULT_INT_FORMAT = Object.assign({}, DEFAULT_NUMERIC_FORMAT)
DEFAULT_INT_FORMAT.precision = 0

export default DEFAULT_NUMERIC_FORMAT
