export default [
  {
    text: 'Today',
    onClick: () => {
      return [
        new Date(this.$moment().startOf('day')),
        new Date(this.$moment().endOf('day'))
      ]
    }
  },
  {
    text: 'Yesterday',
    onClick: () => {
      return [
        new Date(
          this.$moment()
            .subtract(1, 'days')
            .startOf('day')
        ),
        new Date(
          this.$moment()
            .subtract(1, 'days')
            .endOf('day')
        )
      ]
    }
  },
  {
    text: 'Last 30 days',
    onClick: () => [
      new Date(
        this.$moment()
          .add(-30, 'day')
          .startOf('day')
      ),
      new Date(this.$moment().endOf('day'))
    ]
  },
  {
    text: 'This week',
    onClick: () => {
      return [
        new Date(
          this.$moment()
            .day(0)
            .startOf('day')
        ),
        new Date(
          this.$moment()
            .day(6)
            .endOf('day')
        )
      ]
    }
  },
  {
    text: 'Last week',
    onClick: () => {
      return [
        new Date(
          this.$moment()
            .day(-7)
            .startOf('day')
        ),
        new Date(
          this.$moment()
            .day(-1)
            .endOf('day')
        )
      ]
    }
  },
  {
    text: 'This month',
    onClick: () => {
      return [
        new Date(this.$moment().startOf('month')),
        new Date(this.$moment().endOf('month'))
      ]
    }
  },
  {
    text: 'Last month',
    onClick: () => {
      return [
        new Date(
          this.$moment()
            .subtract(1, 'months')
            .startOf('month')
        ),
        new Date(
          this.$moment()
            .subtract(1, 'months')
            .endOf('month')
        )
      ]
    }
  },
  {
    text: 'This year',
    onClick: () => {
      return [
        new Date(this.$moment().startOf('year')),
        new Date(this.$moment().endOf('year'))
      ]
    }
  },
  {
    text: 'Last year',
    onClick: () => {
      return [
        new Date(
          this.$moment()
            .subtract(1, 'years')
            .startOf('year')
        ),
        new Date(
          this.$moment()
            .subtract(1, 'years')
            .endOf('year')
        )
      ]
    }
  }
]
