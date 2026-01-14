import { DataTypeUtil } from '@/services/ds/data/DataTypes'
import cloneDeep from 'lodash/cloneDeep'
import { DEFAULT_STATE_BIN } from '@/components/widgets/elements/table/grouping/ColumnSettingsConfig'
import { AXIS } from '@/components/visualizationBuilder/VisualizationBuilderTypes'
import { TYPES } from '@/components/widgets/elements/chart/ChartConfig'
export const BINNING_TYPES = {
  UNIFORM: 'uniform',
  AUTO: 'auto'
}

export const createBinColumnAlias = (name, template = '') => {
  return template ? `${name}_${template}` : `${name}_bin`
}

export const createBinType = (type) => {
  return `${type}_bin`
}

export const buildBinFromConfig = (config, column, template = '') => {
  let {name, type} = column
  let bin = {
    column: {
      name,
      type
    },
    alias: createBinColumnAlias(name, template),
    options: {
      alg: config.binningType
    }
  }
  if (bin.options.alg === BINNING_TYPES.AUTO) {
    bin.options.numOfBins = Number(config.expected)
    if (DataTypeUtil.isNumeric(type)) {
      bin.options.nice = config.nice
    }
  } else if (bin.options.alg === BINNING_TYPES.UNIFORM) {
    if (DataTypeUtil.isTemporal(type)) {
      bin.options.uniform = {
        width: Number(config.width),
        unit: config.unit
      }
    } else {
      bin.options.uniform = {
        width: Number(config.width)
      }
      bin.options.nice = config.nice
    }
  } else {
    console.error(`Not support binning type ${bin.options.alg}`)
    return null
  }
  return bin
}

export const buildBinObj = (column) => {
  const isTemporal = DataTypeUtil.isTemporal(column.type)
  const binOptions = cloneDeep(DEFAULT_STATE_BIN[isTemporal ? 'auto_temporal' : 'auto_numeric'])
  return buildBinFromConfig(binOptions, column) || {}
}

export const hasBinningAccept = (column) => {
  if (!column.type) return false
  return DataTypeUtil.isTemporal(column.type) || DataTypeUtil.isNumeric(column.type)
}

export const createBinColumnAliasInAxis = (seriesItem, column, axis) => {
  let alias = ''
  if (axis === AXIS.X) {
    alias = createBinColumnAlias(column.name)
  } else if (axis === AXIS.Y) {
    if (seriesItem.type === TYPES.BUBBLE) {
      alias = createBinColumnAlias(column.name)
    } else {
      alias = createBinColumnAlias(column.name, `${seriesItem.id}_bin`)
    }
  }
  return alias
}
