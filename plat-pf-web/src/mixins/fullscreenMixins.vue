<script>
export default {
  data() {
    return {
      documentElement: document.documentElement
    }
  },
  methods: {
    isInFullscreen() {
      return (
        (document.fullscreenElement && document.fullscreenElement !== null) ||
        (document.webkitFullscreenElement &&
          document.webkitFullscreenElement !== null) ||
        (document.mozFullScreenElement &&
          document.mozFullScreenElement !== null) ||
        (document.msFullscreenElement && document.msFullscreenElement !== null)
      )
    },
    requestFullscreen() {
      if (!this.isInFullscreen()) {
        if (this.documentElement.requestFullscreen) {
          this.documentElement.requestFullscreen()
        } else if (this.documentElement.mozRequestFullScreen) {
          this.documentElement.mozRequestFullScreen()
        } else if (this.documentElement.webkitRequestFullScreen) {
          this.documentElement.webkitRequestFullScreen()
        } else if (this.documentElement.msRequestFullscreen) {
          this.documentElement.msRequestFullscreen()
        }
      }
    },
    exitFullscreen() {
      if (this.isInFullscreen()) {
        if (document.exitFullscreen) {
          document.exitFullscreen()
        } else if (document.webkitExitFullscreen) {
          document.webkitExitFullscreen()
        } else if (document.mozCancelFullScreen) {
          document.mozCancelFullScreen()
        } else if (document.msExitFullscreen) {
          document.msExitFullscreen()
        }
      }
    }
  }
}
</script>
