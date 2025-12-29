let mockData = {
  movementDown: {
    cols: [
      {
        name: 'brand',
        type: 'string'
      },
      {
        name: 'current',
        type: 'number'
      },
      {
        name: 'prior',
        type: 'number'
      },
      {
        name: '%',
        type: 'number'
      }
    ],
    rows: [
      [
        'Adidas',
        2,
        4,
        -50
      ],
      [
        'Arborwear',
        15,
        28,
        -46
      ],
      [
        'Baffin',
        0,
        16,
        -100
      ],
      [
        'Bailey/Kangol',
        0,
        1,
        -100
      ],
      [
        'Bates',
        0,
        1,
        -100
      ]
    ]
  },
  movementUp: {
    cols: [
      {
        name: 'brand',
        type: 'string'
      },
      {
        name: 'current',
        type: 'number'
      },
      {
        name: 'prior',
        type: 'number'
      },
      {
        name: '%',
        type: 'number'
      }
    ],
    rows: [
      [
        'Adidas Five Ten',
        3,
        0,
        100
      ],
      [
        'Altra CA',
        6,
        0,
        100
      ],
      [
        `Arm's Reach`,
        26,
        0,
        100
      ],
      [
        'Asics',
        606,
        295,
        105
      ],
      [
        'Belleville/Tactical Research',
        110,
        29,
        280
      ]
    ]
  },
  salesComparison: {
    cols: [
      {
        name: 'brand',
        type: 'string'
      },
      {
        name: '1-17-2021',
        type: 'number'
      },
      {
        name: '1-17-2020',
        type: 'number'
      },
      {
        name: 'diffUnits',
        type: 'number'
      },
      {
        name: '1-17-2021-value',
        type: 'number'
      },
      {
        name: '1-17-2020-value',
        type: 'number'
      },
      {
        name: 'diffUnits-value',
        type: 'number'
      }
    ],
    rows: [
      [
        'thorogood',
        606,
        295,
        105,
        41000,
        19000,
        114
      ],
      [
        'thenorthface',
        373,
        175,
        113,
        66000,
        32000,
        103
      ],
      [
        'asics',
        332,
        481,
        -30,
        33000,
        48000,
        -33
      ],
      [
        'danner',
        208,
        258,
        -29,
        6000,
        8000,
        -27
      ],
      [
        'muckboots',
        158,
        11,
        1336,
        8000,
        600,
        1300
      ]
    ]
  },
  daySalesNum: {
    cols: [
      {
        name: 'brand',
        type: 'string'
      },
      {
        name: 'current',
        type: 'number'
      },
      {
        name: 'currentSegments',
        type: 'number'
      },
      {
        name: 'prior',
        type: 'number'
      }
    ],
    rows: [
      [
        'thorogood',
        350600,
        -4,
        600000
      ],
      [
        'thenorthface',
        350600,
        53,
        680000
      ],
      [
        'asics',
        150600,
        5,
        900000
      ],
      [
        'danner',
        350600,
        45,
        600000
      ],
      [
        'muckboots',
        350600,
        4,
        600000
      ]
    ]
  },
  daySales: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'MFN',
        type: 'number'
      },
      {
        name: 'INV',
        type: 'number'
      },
      {
        name: 'prime',
        type: 'number'
      },
      {
        name: 'total',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-15',
        3506,
        5500,
        6000,
        6500
      ],
      [
        '12-16',
        3506,
        5300,
        6800,
        9500
      ],
      [
        '12-17',
        1506,
        5500,
        9000,
        10000
      ],
      [
        '12-18',
        3600,
        4000,
        6000,
        6500
      ],
      [
        '12-19',
        3060,
        4000,
        6000,
        6500
      ]
    ]
  },
  allOrders: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'MFN',
        type: 'number'
      },
      {
        name: 'INV',
        type: 'number'
      },
      {
        name: 'prime',
        type: 'number'
      },
      {
        name: 'allSales',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-15',
        3506,
        5500,
        6000,
        6500
      ],
      [
        '12-16',
        3506,
        5300,
        6800,
        9500
      ],
      [
        '12-17',
        1506,
        5500,
        9000,
        5000
      ],
      [
        '12-18',
        3600,
        4000,
        6000,
        6500
      ],
      [
        '12-19',
        3060,
        4000,
        6000,
        6500
      ]
    ]
  },
  saleOf30Day: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'priormonth',
        type: 'number'
      },
      {
        name: '2021',
        type: 'number'
      },
      {
        name: '2020',
        type: 'number'
      },
      {
        name: '2019',
        type: 'number'
      },
      {
        name: '2018',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-15',
        350600,
        550000,
        600000,
        650000,
        405060
      ],
      [
        '12-16',
        350600,
        530000,
        680000,
        950000,
        346564
      ],
      [
        '12-17',
        150600,
        550000,
        900000,
        550000,
        345464
      ],
      [
        '12-18',
        350600,
        450000,
        600000,
        650000,
        344364
      ],
      [
        '12-19',
        350600,
        450000,
        600000,
        650000,
        354589
      ]
    ]
  },
  orderProductSales: {
    cols: [
      {
        name: 'fulfillment_type',
        type: 'string'
      },
      {
        name: 'value',
        type: 'value'
      }
    ],
    rows: [
      [
        'INV',
        80
      ],
      [
        'DS',
        10
      ],
      [
        'RA',
        2
      ],
      [
        'Prime',
        8
      ]
    ]
  },
  repricingInstance: {
    cols: [
      {
        name: 'date',
        type: 'date'
      },
      {
        name: 'value',
        type: 'value'
      }
    ],
    rows: [
      [
        '2021-01-09T21:47:56+07:00',
        1229253
      ],
      [
        '2021-01-02T21:59:06+07:00',
        1739056
      ],
      [
        '2020-12-30T21:17:43+07:00',
        1499353
      ],
      [
        '2020-12-29T16:03:36+07:00',
        1023838
      ],
      [
        '2020-12-24T18:42:32+07:00',
        1474069
      ],
      [
        '2020-12-30T20:06:09+07:00',
        1714116
      ],
      [
        '2020-12-21T16:20:10+07:00',
        1820077
      ],
      [
        '2020-12-22T09:15:16+07:00',
        1487989
      ],
      [
        '2020-12-26T22:31:54+07:00',
        1622919
      ],
      [
        '2021-01-09T01:39:19+07:00',
        1061536
      ],
      [
        '2020-12-17T21:38:10+07:00',
        1465850
      ],
      [
        '2020-12-28T22:54:00+07:00',
        1242586
      ],
      [
        '2020-12-24T20:29:54+07:00',
        1394087
      ],
      [
        '2021-01-11T10:54:55+07:00',
        1541307
      ],
      [
        '2020-12-28T22:56:38+07:00',
        1364737
      ],
      [
        '2020-12-26T06:29:44+07:00',
        1711101
      ],
      [
        '2020-12-28T07:10:43+07:00',
        1631028
      ],
      [
        '2021-01-03T09:02:51+07:00',
        1916919
      ],
      [
        '2020-12-22T07:30:06+07:00',
        1752107
      ],
      [
        '2020-12-15T20:02:03+07:00',
        1788118
      ]
    ]
  },
  allSales: {
    cols: [
      {
        name: 'brand',
        type: 'string'
      },
      {
        name: '1-12',
        type: 'number'
      },
      {
        name: '1-11',
        type: 'number'
      },
      {
        name: '1-10',
        type: 'number'
      },
      {
        name: '1-9',
        type: 'number'
      },
      {
        name: '1-8',
        type: 'number'
      },
      {
        name: '1-7',
        type: 'number'
      },
      {
        name: '1-6',
        type: 'number'
      },
      {
        name: '1-5',
        type: 'number'
      },
      {
        name: '1-4',
        type: 'number'
      },
      {
        name: '1-3',
        type: 'number'
      },
      {
        name: '30day',
        type: 'number'
      },
      {
        name: '30avg',
        type: 'number'
      },
      {
        name: 'dec',
        type: 'number'
      },
      {
        name: 'nov',
        type: 'number'
      },
      {
        name: 'oct',
        type: 'number'
      }
    ],
    rows: [
      [
        'Danner',
        2,
        5,
        8,
        4,
        2,
        1,
        2,
        5,
        4,
        2,
        101,
        3.37,
        119,
        171,
        256
      ],
      [
        'Grundens',
        2,
        6,
        3,
        2,
        0,
        2,
        2,
        1,
        1,
        1,
        71,
        2.37,
        121,
        183,
        348
      ],
      [
        'Adidas',
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        15,
        0.50,
        31,
        22,
        17
      ],
      [
        'Adidas',
        107,
        99,
        105,
        112,
        109,
        114,
        115,
        118,
        134,
        165,
        3881,
        129.37,
        5294,
        4376,
        4930
      ],
      [
        'The North Face',
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        15,
        0.50,
        31,
        22,
        17
      ],
      [
        'Haggar',
        0,
        0,
        0,
        0,
        0,
        1,
        1,
        0,
        0,
        0,
        15,
        0.50,
        31,
        22,
        17
      ]
    ]
  },
  totalInven: {
    cols: [
      {
        name: 'brand',
        type: 'string'
      },
      {
        name: 'inventory',
        type: 'number'
      },
      {
        name: 'invenMoh',
        type: 'number'
      },
      {
        name: 'amazon30day',
        type: 'number'
      },
      {
        name: 'amazonToday',
        type: 'number'
      },
      {
        name: 'amazonValue',
        type: 'number'
      },
      {
        name: 'amazonSKU',
        type: 'number'
      },
      {
        name: 'amazonUnits',
        type: 'number'
      },
      {
        name: 'amazonUnitsMoh',
        type: 'number'
      },
      {
        name: 'SKU30day',
        type: 'number'
      },
      {
        name: 'SKUToday',
        type: 'number'
      },
      {
        name: 'SKUValue',
        type: 'number'
      },
      {
        name: 'SKU',
        type: 'number'
      },
      {
        name: 'SKUUnits',
        type: 'number'
      },
      {
        name: 'SKUMoh',
        type: 'number'
      }
    ],
    rows: [
      [
        'Danner',
        2000000,
        1.67,
        8000,
        400,
        1800000,
        2600,
        12000,
        1.23,
        732,
        10,
        404000,
        1037,
        5300,
        7.64
      ],
      [
        'Grundens',
        2000000,
        1.67,
        8000,
        400,
        1800000,
        2600,
        12000,
        1.23,
        732,
        10,
        404000,
        1037,
        5300,
        7.64
      ],
      [
        'Adidas',
        2000000,
        1.67,
        8000,
        400,
        1800000,
        2600,
        12000,
        1.23,
        732,
        10,
        404000,
        1037,
        5300,
        7.64
      ],
      [
        'Adidas',
        2000000,
        1.67,
        8000,
        400,
        1800000,
        2600,
        12000,
        1.23,
        732,
        10,
        404000,
        1037,
        5300,
        7.64
      ],
      [
        'The North Face',
        2000000,
        1.67,
        8000,
        400,
        1800000,
        2600,
        12000,
        1.23,
        732,
        10,
        404000,
        1037,
        5300,
        7.64
      ],
      [
        'Haggar',
        2000000,
        1.67,
        8000,
        400,
        1800000,
        2600,
        12000,
        1.23,
        732,
        10,
        404000,
        1037,
        5300,
        7.64
      ]
    ]
  },
  invenMohValue: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'total',
        type: 'number'
      },
      {
        name: 'FBA',
        type: 'number'
      },
      {
        name: 'SKUVaults',
        type: 'number'
      }
    ],
    rows: [
      [
        'Jan 2020',
        200,
        0,
        100
      ],
      [
        'Feb 2020',
        350,
        0,
        100
      ],
      [
        `Mar 2020`,
        260,
        0,
        100
      ],
      [
        'Apr 2020',
        606,
        295,
        105
      ],
      [
        'May 2020',
        310,
        29,
        280
      ],
      [
        'Jun 2020',
        410,
        230,
        280
      ],
      [
        'Jul 2020',
        310,
        290,
        280
      ],
      [
        'Aug 2020',
        310,
        29,
        280
      ],
      [
        'Sep 2020',
        210,
        29,
        280
      ],
      [
        'Oct 2020',
        110,
        29,
        280
      ],
      [
        'Nov 2020',
        410,
        29,
        280
      ],
      [
        'Dec 2020',
        310,
        29,
        280
      ]
    ]
  },
  earnTurnRatio: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'total',
        type: 'number'
      },
      {
        name: '6Mo',
        type: 'number'
      },
      {
        name: '9Mo',
        type: 'number'
      },
      {
        name: '12Mo',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-15',
        850600,
        550000,
        600000,
        650000
      ],
      [
        '12-16',
        1050600,
        530000,
        680000,
        950000
      ],
      [
        '12-17',
        950600,
        550000,
        900000,
        550000
      ],
      [
        '12-18',
        750600,
        450000,
        600000,
        650000
      ],
      [
        '12-19',
        750600,
        450000,
        600000,
        650000
      ]
    ]
  },
  etGraph: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'active',
        type: 'number'
      },
      {
        name: 'outdoor',
        type: 'number'
      },
      {
        name: 'lifestyle',
        type: 'number'
      },
      {
        name: 'work',
        type: 'number'
      },
      {
        name: 'co',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-15',
        350,
        550,
        600,
        600,
        405
      ],
      [
        '12-16',
        350,
        530,
        680,
        950,
        346
      ],
      [
        '12-17',
        150,
        550,
        900,
        550,
        345
      ],
      [
        '12-18',
        350,
        450,
        600,
        650,
        344
      ],
      [
        '12-19',
        350,
        400,
        600,
        600,
        389
      ]
    ]
  },
  MFNCategory: {
    cols: [
      {
        name: 'segments',
        type: 'string'
      },
      {
        name: 'MTD',
        type: 'number'
      },
      {
        name: 'december',
        type: 'number'
      },
      {
        name: 'decemberSegment',
        type: 'number'
      },
      {
        name: 'november',
        type: 'number'
      }
    ],
    rows: [
      [
        'Active',
        80,
        550,
        1000,
        -16,
        405
      ],
      [
        'Lifestyle',
        70,
        550,
        12000,
        73,
        405
      ],
      [
        'Outdoor',
        55,
        550,
        3000,
        -25,
        405
      ],
      [
        'Work',
        65,
        550,
        7500,
        -9,
        405
      ]
    ]
  },
  MFNCategoryLine: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'active',
        type: 'number'
      },
      {
        name: 'outdoor',
        type: 'number'
      },
      {
        name: 'fashion',
        type: 'number'
      },
      {
        name: 'work',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-19',
        80,
        550,
        100,
        16,
        405
      ],
      [
        '12-20',
        70,
        550,
        120,
        73,
        405
      ],
      [
        '12-21',
        55,
        550,
        300,
        25,
        405
      ],
      [
        '12-22',
        65,
        550,
        750,
        9,
        405
      ],
      [
        '12-23',
        65,
        550,
        750,
        9,
        405
      ],
      [
        '12-24',
        65,
        550,
        700,
        9,
        405
      ],
      [
        '12-25',
        65,
        550,
        750,
        9,
        405
      ],
      [
        '12-26',
        65,
        550,
        750,
        9,
        405
      ],
      [
        '12-27',
        65,
        550,
        700,
        9,
        405
      ],
      [
        '12-28',
        65,
        550,
        700,
        9,
        405
      ],
      [
        '12-29',
        65,
        550,
        750,
        9,
        405
      ],
      [
        '12-30',
        65,
        550,
        700,
        9,
        405
      ],
      [
        '12-31',
        65,
        550,
        750,
        9,
        405
      ],
      [
        '1-1',
        65,
        550,
        700,
        9,
        405
      ],
      [
        '1-2',
        65,
        550,
        700,
        9,
        405
      ],
      [
        '1-3',
        65,
        550,
        750,
        9,
        405
      ]
    ]
  },
  totalRAOrder30Days: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'NC',
        type: 'number'
      },
      {
        name: 'Utah',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-20',
        80,
        550
      ],
      [
        '12-21',
        80,
        550
      ],
      [
        '12-22',
        80,
        550
      ],
      [
        '12-23',
        80,
        550
      ],
      [
        '12-24',
        100,
        16
      ],
      [
        '12-25',
        80,
        550
      ],
      [
        '12-26',
        80,
        550
      ],
      [
        '12-27',
        80,
        550
      ],
      [
        '12-28',
        80,
        550
      ],
      [
        '12-29',
        80,
        16
      ],
      [
        '12-30',
        80,
        550
      ],
      [
        '12-31',
        80,
        16
      ],
      [
        '1-1',
        80,
        550
      ]
    ]
  },
  averageSalesPrice: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'price',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-20',
        80
      ],
      [
        '12-21',
        40
      ],
      [
        '12-22',
        30
      ],
      [
        '12-23',
        60
      ],
      [
        '12-24',
        50
      ],
      [
        '12-25',
        80
      ],
      [
        '12-26',
        110
      ],
      [
        '12-27',
        100
      ],
      [
        '12-28',
        80
      ],
      [
        '12-29',
        20
      ],
      [
        '12-30',
        30
      ],
      [
        '12-31',
        40
      ],
      [
        '1-1',
        60
      ]
    ]
  },
  handlingTime: {
    cols: [
      {
        name: 'brand',
        type: 'string'
      },
      {
        name: 'currentHT',
        type: 'number'
      },
      {
        name: 'prevHT',
        type: 'number'
      }
    ],
    rows: [
    ]
  },
  storeOnlineSale: {
    cols: [
      {
        name: 'date',
        type: 'string'
      },
      {
        name: 'net',
        type: 'number'
      },
      {
        name: 'returns',
        type: 'number'
      },
      {
        name: 'profit',
        type: 'number'
      },
      {
        name: 'googleSpent',
        type: 'number'
      },
      {
        name: 'gross',
        type: 'number'
      }
    ],
    rows: [
      [
        '12-19',
        80,
        150,
        400,
        16,
        405,
        600
      ],
      [
        '12-20',
        70,
        250,
        320,
        73,
        405,
        600
      ],
      [
        '12-21',
        55,
        150,
        170,
        25,
        405,
        600
      ],
      [
        '12-22',
        340,
        250,
        350,
        9,
        405,
        600
      ],
      [
        '12-23',
        165,
        50,
        750,
        9,
        405,
        600
      ],
      [
        '12-24',
        65,
        50,
        700,
        9,
        405,
        600
      ],
      [
        '12-25',
        105,
        40,
        750,
        9,
        405,
        600
      ],
      [
        '12-26',
        65,
        550,
        750,
        9,
        405,
        600
      ],
      [
        '12-27',
        105,
        40,
        750,
        9,
        405,
        600
      ],
      [
        '12-28',
        165,
        50,
        750,
        9,
        405,
        600
      ],
      [
        '12-29',
        65,
        123,
        700,
        9,
        40,
        60
      ],
      [
        '12-30',
        65,
        550,
        700,
        9,
        405,
        600
      ],
      [
        '12-31',
        65,
        550,
        750,
        9,
        214,
        345
      ],
      [
        '1-1',
        65,
        123,
        700,
        9,
        40,
        60
      ],
      [
        '1-2',
        65,
        127,
        700,
        9,
        405,
        600
      ],
      [
        '1-3',
        65,
        100,
        750,
        9,
        405,
        600
      ]
    ]
  }
}

export default mockData
