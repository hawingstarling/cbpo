import $ from 'jquery'
import maxBy from 'lodash/maxBy'

let SCROLL_WIDTH = null

const calcWidthOfScrollBar = () => {
  let $outer = $('<div class="beauty-scrollbar">').css({ visibility: 'hidden', width: 100, overflow: 'scroll' }).appendTo('body')
  let widthWithScroll = $('<div>').css({ width: '100%' }).appendTo($outer).outerWidth()
  $outer.remove()
  return 100 - widthWithScroll
}

export const getWidthOfScrollBar = () => {
  if (SCROLL_WIDTH === null) {
    SCROLL_WIDTH = calcWidthOfScrollBar()
  }
  return SCROLL_WIDTH
}

export const getTextWidth = (text, isBold = false) => {
  let width = 0
  const textElement = document.createElement('span')
  document.body.appendChild(textElement)

  textElement.style.visibility = 'hidden'
  textElement.style.fontSize = '11px'
  textElement.style.height = 'auto'
  textElement.style.width = 'auto'
  textElement.style.position = 'absolute'
  textElement.style.whiteSpace = 'no-wrap'
  textElement.innerHTML = text
  isBold && (textElement.style.fontWeight = 'bold')

  width = Math.ceil(textElement.clientWidth)
  textElement.remove()

  return width
}

export const findLongestWord = (string) => {
  let strSplit = string.split(/\s+/)
  return maxBy(strSplit, 'length')
}
