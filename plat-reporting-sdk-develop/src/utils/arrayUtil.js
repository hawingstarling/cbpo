import {cloneDeep} from 'lodash'

export const moveElement = (arr, from, to) => {
  arr = cloneDeep(arr)
  const newPosition = from < to ? (to - 1) : to
  arr.splice(newPosition, 0, arr.splice(from, 1)[0])
  return arr
}
