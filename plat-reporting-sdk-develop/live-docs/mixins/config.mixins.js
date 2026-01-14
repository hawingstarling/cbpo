const configMixins = Vue.component('configMixins', {
  data() {
    return {
      templates: [],
      dataSource: {
        cols: [
          {'name': 'seller_name', 'type': 'string'},
          {'name': 'sku', 'type': 'string'},
          {'name': 'upc/ean', 'type': 'string'},
          {'name': 'asin', 'type': 'string'},
          {'name': 'title', 'type': 'string'},
          {'name': 'seller_price', 'type': 'number'},
          {'name': 'map_price', 'type': 'number'},
          {'name': 'diff', 'type': 'number'},
          {'name': 'diff_percent', 'type': 'number'},
          {'name': 'link', 'type': 'string'},
          {'name': 'screenshot', 'type': 'string'},
          {'name': 'captured_at', 'type': 'date'},
          {'name': 'fba', 'type': 'boolean'},
          {'name': 'prime', 'type': 'boolean'},
          {'name': 'condition', 'type': 'string'},
          {'name': 'rating', 'type': 'int'},
          {'name': 'growth_value', 'type': 'string'},
          {'name': 'override', 'type': 'string'}
        ],
        rows: [
          ['Amazon.com', 'TG-804-4810_12-M', '014799962616', 'B00TEFEXAK', 'Thorogood Men\'s Wellington 8\' Safety Toe-M,  Brown,  12 M US', 119.36, 149.95, 30.59, 20.4, 'https://www.amazon.com/gp/offer-listing/B00TEFEXAK/ref=olp_twister_child?ie=UTF8&seller=ATVPDKIKX0DER&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604c3d01763b0028f44830--2020-03-04--19-48-13--est.jpg', '2020-03-05T00:48:25.071Z', true, true, 'New'],
          ['Amazon.com', 'TG-804-4810_13-W', '014799962760', 'B00TEFF0E8', 'Thorogood Men\'s Wellington 8\' Safety Toe-M,  Brown,  13 W US', 131.21, 149.95, 18.74, 12.5, 'https://www.amazon.com/gp/offer-listing/B00TEFF0E8/ref=olp_twister_child?ie=UTF8&seller=ATVPDKIKX0DER&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604c63066a750013f69518--2020-03-04--19-48-51--est.jpg', '2020-03-05T00:48:55.571Z', true, true, 'New'],
          ['Andrea Sport Shop', 'TG-534-6906_8-M', '014799721558', 'B001RPDQQW', 'Thorogood 534-6906 Women\'s Soft Streets Series 6\' Plain Toe Chukka Boot,  Black - 8 B(M) US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B001RPDQQW/ref=olp_twister_child?ie=UTF8&seller=A1E0M68J5LX6HF&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60456e5f7d470021d24e2f--2020-03-04--19-19-59--est.jpg', '2020-03-05T00:20:00.360Z', false, false, 'New'],
          ['Andrea Sport Shop', 'TG-834-6907_11-XW', '014799717872', 'B001RR7KSU', 'Thorogood 834-6907 Men\'s Soft Streets Series Moc Toe Oxford,  Black - 11 XW', 129.95, 134.95, 5, 3.71, 'https://www.amazon.com/gp/offer-listing/B001RR7KSU/ref=olp_twister_child?ie=UTF8&seller=A1E0M68J5LX6HF&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604993b6c6cc0052692ce4--2020-03-04--19-36-57--est.jpg', '2020-03-05T00:37:04.545Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_8.5-M', '840777101032', 'B01E8N2C6E', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 8.5 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2C6E/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6049e23f0c94002f07f627--2020-03-04--19-38-10--est.jpg', '2020-03-05T00:38:13.768Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_8.5-W', '840777101179', 'B01E8N2WQ4', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 8.5 2E US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2WQ4/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604a18b6c6cc0052692d6e--2020-03-04--19-38-58--est.jpg', '2020-03-05T00:38:58.978Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_9-M', '840777101049', 'B01E8N2DH2', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 9 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2DH2/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604a2cb6c6cc0052692d81--2020-03-04--19-39-16--est.jpg', '2017-03-05T00:39:16.596Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_9.5-M', '840777101056', 'B01E8N2ERG', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 9.5 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2ERG/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604a3db6c6cc0052692d92--2020-03-04--19-39-32--est.jpg', '2020-03-05T00:39:36.771Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_9.5-W', '840777101193', 'B01E8N2ZEI', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 9.5 2E US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2ZEI/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604a5b30d5710033f66f83--2020-03-04--19-40-04--est.jpg', '2020-03-05T00:40:04.535Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_10-M', '840777101063', 'B01E8N2GJW', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 10 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2GJW/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604a7130d5710033f66f9d--2020-03-04--19-40-41--est.jpg', '2017-03-05T00:40:55.013Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_10.5-M', '840777101070', 'B01E8N2I1S', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 10.5 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2I1S/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604ab230d5710033f66ff1--2020-03-04--19-41-38--est.jpg', '2020-03-05T00:41:43.104Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_10.5-W', '840777101216', 'B01E8N31UK', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 10.5 2E US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N31UK/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604af1066a750013f6934f--2020-03-04--19-43-16--est.jpg', '2020-03-05T00:43:17.741Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_11.5-M', '840777101094', 'B01E8N2L2E', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 11.5 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2L2E/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604b43ed486b0021d96658--2020-03-04--19-44-03--est.jpg', '2017-03-05T00:44:04.566Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_11.5-W', '840777101230', 'B01E8N34JS', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 11.5 2E US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N34JS/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604b635f7d470021d254f6--2020-03-04--19-44-45--est.jpg', '2017-03-05T00:45:15.904Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_13-M', '840777101117', 'B01E8N2NI6', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 13 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2NI6/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604ba830d5710033f6711b--2020-03-04--19-45-36--est.jpg', '2017-03-05T00:45:36.827Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_14-M', '840777101124', 'B01E8N2P2U', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 14 B(M) US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N2P2U/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604bbd5f7d470021d25575--2020-03-04--19-46-09--est.jpg', '2020-03-05T00:46:17.106Z', false, false, 'New'],
          ['GoBros', 'TG-804-3165_14-W', '840777101261', 'B01E8N38CQ', 'Thorogood 804-3165 Men\'s Thoro-Flex 6\' Waterproof Composite Safety Toe Sport Boot,  Trail Crazyhorse - 14 2E US', 114, 129.95, 15.95, 12.27, 'https://www.amazon.com/gp/offer-listing/B01E8N38CQ/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604bf4b6c6cc0052692fd4--2020-03-04--19-46-58--est.jpg', '2020-03-05T00:47:24.296Z', false, false, 'New'],
          ['GoBros', 'TG-804-4448_9.5-W', '014799868864', 'B007KJ7BB0', 'Thorogood 804-4448 Men\'s Gen-flex2 8\' Insulated Waterproof Composite Safety Toe Boot,  Brown - 9.5 W', 132, 149.95, 17.95, 11.97, 'https://www.amazon.com/gp/offer-listing/B007KJ7BB0/ref=olp_twister_child?ie=UTF8&seller=A1469MBVCFUJHZ&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604eedb6c6cc0052693340--2020-03-04--19-59-34--est.jpg', '2020-03-05T00:59:35.210Z', false, false, 'New'],
          ['GreatFinds4You!!', 'TG-534-6905_8-M', '014799713430', 'B001WLEIPE', 'Thorogood Women\'s Soft Streets Oxford, Black, 8 M US', 65, 129.95, 64.95, 49.98, 'https://www.amazon.com/gp/offer-listing/B001WLEIPE/ref=olp_twister_child?ie=UTF8&seller=A390ZKCLKC62GR&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60455730d5710033f669dd--2020-03-04--19-18-38--est.jpg', '2020-03-05T00:18:39.467Z', false, false, 'New'],
          ['GreatFinds4You!!', 'TG-834-6908_10-M', '014799712976', 'B000I7C7QK', 'Thorogood 834-6908 Men\'s Soft Streets Series Double Track Oxford,  Black - 10 D(M) US', 99, 134.95, 35.95, 26.64, 'https://www.amazon.com/gp/offer-listing/B000I7C7QK/ref=olp_twister_child?ie=UTF8&seller=A390ZKCLKC62GR&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6049c6b6c6cc0052692d15--2020-03-04--19-37-41--est.jpg', '2020-03-05T00:37:43.667Z', false, false, 'New'],
          ['GreenKeys,  LLC', 'TG-161-0300_L', '014799614614', 'B007RTBNGW', 'Thorogood 161-0300 Men\'s Avalanche 11\' Waterproof Overshoe,  Black - Large', 76.13, 78.95, 2.82, 3.57, 'https://www.amazon.com/gp/offer-listing/B007RTBNGW/ref=olp_twister_child?ie=UTF8&seller=A1B6QBLJWGCZW2&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60453a01763b0028f44036--2020-03-04--19-18-09--est.jpg', '2020-03-05T00:18:10.168Z', true, true, 'New'],
          ['Maxmerchant', 'TG-834-6027_6-M', '014799777708', 'B001RQHN3I', 'Thorogood Men\'s Classic Leather Oxford Shoe,  Black - 6 M', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B001RQHN3I/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6046e430d5710033f66bac--2020-03-04--19-25-17--est.jpg', '2020-03-05T00:25:17.669Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_6.5-M', '014799777715', 'B003HOX73S', 'Thorogood Men\'s Classic Leather Oxford Shoe- 6.5 M Black', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B003HOX73S/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6046f5b6c6cc00526929bf--2020-03-04--19-25-37--est.jpg', '2020-03-05T00:25:37.969Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_7-M', '014799261504', 'B000I7FVZY', 'Thorogood Men\'s Classic Leather Oxford Shoe,  Black - 7 M', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7FVZY/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60472330d5710033f66c03--2020-03-04--19-26-23--est.jpg', '2020-03-05T00:26:28.826Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_7.5-M', '014799261511', 'B000I7E2K4', 'Thorogood Men\'s Classic Leather Oxford Shoe- 7.5 M Black', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7E2K4/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60473e650eb50013f9e500--2020-03-04--19-26-44--est.jpg', '2020-03-05T00:26:45.198Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_8-M', '014799261528', 'B000I7FW12', 'Thorogood Men\'s Classic Leather Oxford Shoe- 8 M Black', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7FW12/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604758066a750013f68f0f--2020-03-04--19-27-22--est.jpg', '2020-03-05T00:27:23.807Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_8.5-M', '0147992615323', 'B000I7FW1M', 'Thorogood Men\'s Classic Leather Oxford Shoe- 8.5 M Black', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7FW1M/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6047763f0c94002f07f3a4--2020-03-04--19-27-45--est.jpg', '2020-03-05T00:27:49.481Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_9-M', '014799261542', 'B000I7FW1W', 'Thorogood Men\'s Classic Leather Oxford Shoe,  Black - 9 M', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7FW1W/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604796ed486b0021d961e6--2020-03-04--19-28-55--est.jpg', '2020-03-05T00:29:10.098Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_9.5-M', '014799261559', 'B000I7H8DC', 'Thorogood Men\'s Classic Leather Oxford Shoe- 9.5 M Black', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7H8DC/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6047e4ed486b0021d96242--2020-03-04--19-29-29--est.jpg', '2018-03-05T00:29:29.443Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_9.5-W', '014799261689', 'B000I7H8K0', 'Thorogood Men\'s Classic Leather Oxford Shoe- 9.5 W Black', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7H8K0/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6047fd01763b0028f4437d--2020-03-04--19-30-03--est.jpg', '2018-03-05T00:30:10.370Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6027_10-M', '014799261566', 'B000I7H8EG', 'Thorogood Men\'s Classic Leather Oxford Shoe- 10 M Black', 104.99, 124.95, 19.96, 15.97, 'https://www.amazon.com/gp/offer-listing/B000I7H8EG/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60482a01763b0028f443b9--2020-03-04--19-31-01--est.jpg', '2018-03-05T00:31:10.405Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_6-M', '014799729141', 'B001RPKQDS', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 6 M', 68.49, 74.95, 6.46, 8.62, 'https://www.amazon.com/gp/offer-listing/B001RPKQDS/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604856650eb50013f9e658--2020-03-04--19-31-38--est.jpg', '2018-03-05T00:31:45.413Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_7.5-M', '014799729172', 'B001RPEA4O', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 7.5 M', 68.49, 74.95, 6.46, 8.62, 'https://www.amazon.com/gp/offer-listing/B001RPEA4O/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60487a066a750013f69064--2020-03-04--19-32-22--est.jpg', '2018-03-05T00:32:27.384Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_8-M', '014799729189', 'B001RQG6VS', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 8 M', 68.49, 74.95, 6.46, 8.62, 'https://www.amazon.com/gp/offer-listing/B001RQG6VS/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6048bbed486b0021d9633d--2020-03-04--19-33-12--est.jpg', '2020-03-05T00:33:15.882Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_8.5-M', '014799729196', 'B001RPZ4VW', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 8.5 M', 69.99, 74.95, 4.96, 6.62, 'https://www.amazon.com/gp/offer-listing/B001RPZ4VW/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6048d330d5710033f66dcf--2020-03-04--19-33-41--est.jpg', '2020-03-05T00:33:57.471Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_9-M', '014799729202', 'B001RR3VA6', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 9 M', 68.49, 74.95, 6.46, 8.62, 'https://www.amazon.com/gp/offer-listing/B001RR3VA6/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604903650eb50013f9e711--2020-03-04--19-34-18--est.jpg', '2020-03-05T00:34:24.319Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_9.5-M', '014799729219', 'B001RQHNBU', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 9.5 M', 69.99, 74.95, 4.96, 6.62, 'https://www.amazon.com/gp/offer-listing/B001RQHNBU/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604924650eb50013f9e736--2020-03-04--19-35-06--est.jpg', '2020-03-05T00:35:12.098Z', false, false, 'New'],
          ['Maxmerchant', 'TG-814-4200_7-D', '014799639426', 'B001QJA6CQ', 'Thorogood Men\'s 814-4200 American Heritage 6\' Moc Toe,  MAXwear Wedge Non-Safety Toe Boot,  Tobacco Oil-Tanned - 7 D US', 134.99, 189.95, 54.96, 28.93, 'https://www.amazon.com/gp/offer-listing/B001QJA6CQ/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604ceb066a750013f695a9--2020-03-04--19-51-08--est.jpg', '2020-03-05T00:51:32.278Z', false, false, 'New'],
          ['MilliKix', 'TG-814-4178_13-D', '840777121351', 'B01N1UFL1W', 'Thorogood 814-4178 Men\'s American Heritage 8\' Moc Toe,  MAXWear Wedge Non-Safety Toe Boot,  13 Medium US Men', 194.95, 199.95, 5, 2.5, 'https://www.amazon.com/gp/offer-listing/B01N1UFL1W/ref=olp_twister_child?ie=UTF8&seller=A27XQSHYXYFFJT&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6063af30d5710033f68b71--2020-03-04--21-28-19--est.jpg', '2020-03-05T02:28:20.184Z', true, true, 'New'],
          ['MilliKix', 'TG-814-4178_8-D', '840777121269', 'B01MT163FM', 'Thorogood 814-4178 Men\'s American Heritage 8\' Moc Toe,  MAXWear Wedge Non-Safety Toe Boot,  Trail Crazyhorse - 8 D(M) US', 194.95, 199.95, 5, 2.5, 'https://www.amazon.com/gp/offer-listing/B01MT163FM/ref=olp_twister_child?ie=UTF8&seller=A27XQSHYXYFFJT&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604cb0066a750013f69570--2020-03-04--19-50-09--est.jpg', '2020-03-05T00:50:13.696Z', true, true, 'New'],
          ['P and R Traders', 'TG-534-6932_6.5-W', '014799826055', 'B002QQ8UDK', 'Thorogood Women\'s Street Athletics Oxford, Black, 6.5 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UDK/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604eb65f7d470021d258d0--2020-03-04--19-58-48--est.jpg', '2020-03-05T00:58:51.372Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_7-W', '014799826062', 'B002QQ8UDU', 'Thorogood Women\'s Street Athletics Oxford, Black, 7 W US', 124.95, 139.95, 15, 10.72, 'https://www.amazon.com/gp/offer-listing/B002QQ8UDU/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6045cf3f0c94002f07f19d--2020-03-04--19-20-45--est.jpg', '2020-03-05T00:20:51.123Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_8-W', '014799826086', 'B002QQ8UEE', 'Thorogood Women\'s Street Athletics Oxford, Black, 8 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UEE/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6045fced486b0021d95fc6--2020-03-04--19-21-33--est.jpg', '2020-03-05T00:21:37.674Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_9.5-W', '014799826116', 'B002QQ8UF8', 'Thorogood Women\'s Street Athletics Oxford, Black, 9.5 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UF8/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60462a066a750013f68d9b--2020-03-04--19-22-20--est.jpg', '2020-03-05T00:22:43.445Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_10-W', '014799826123', 'B002QQ8UFS', 'Thorogood Women\'s Street Athletics Oxford, Black, 10 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UFS/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60466a3f0c94002f07f255--2020-03-04--19-23-11--est.jpg', '2020-03-05T00:23:11.725Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_11-W', '014799826130', 'B002QQ8UG2', 'Thorogood Women\'s Street Athletics Oxford, Black, 11 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UG2/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604684ed486b0021d96086--2020-03-04--19-23-54--est.jpg', '2020-03-05T00:24:04.696Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_9-M', '014799729202', 'B001RR3VA6', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 9 M', 68.49, 74.95, 6.46, 8.62, 'https://www.amazon.com/gp/offer-listing/B001RR3VA6/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604903650eb50013f9e711--2020-03-04--19-34-18--est.jpg', '2019-03-05T00:34:24.319Z', false, false, 'New'],
          ['Maxmerchant', 'TG-834-6041_9.5-M', '014799729219', 'B001RQHNBU', 'Thorogood Men\'s 834-6041 Plain Toe Leather Oxford,  Black - 9.5 M', 69.99, 74.95, 4.96, 6.62, 'https://www.amazon.com/gp/offer-listing/B001RQHNBU/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604924650eb50013f9e736--2020-03-04--19-35-06--est.jpg', '2019-03-05T00:35:12.098Z', false, false, 'New'],
          ['Maxmerchant', 'TG-814-4200_7-D', '014799639426', 'B001QJA6CQ', 'Thorogood Men\'s 814-4200 American Heritage 6\' Moc Toe,  MAXwear Wedge Non-Safety Toe Boot,  Tobacco Oil-Tanned - 7 D US', 134.99, 189.95, 54.96, 28.93, 'https://www.amazon.com/gp/offer-listing/B001QJA6CQ/ref=olp_twister_child?ie=UTF8&seller=A14MD2C5I7GW3A&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604ceb066a750013f695a9--2020-03-04--19-51-08--est.jpg', '2020-03-05T00:51:32.278Z', false, false, 'New'],
          ['MilliKix', 'TG-814-4178_13-D', '840777121351', 'B01N1UFL1W', 'Thorogood 814-4178 Men\'s American Heritage 8\' Moc Toe,  MAXWear Wedge Non-Safety Toe Boot,  13 Medium US Men', 194.95, 199.95, 5, 2.5, 'https://www.amazon.com/gp/offer-listing/B01N1UFL1W/ref=olp_twister_child?ie=UTF8&seller=A27XQSHYXYFFJT&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6063af30d5710033f68b71--2020-03-04--21-28-19--est.jpg', '2020-03-05T02:28:20.184Z', true, true, 'New'],
          ['MilliKix', 'TG-814-4178_8-D', '840777121269', 'B01MT163FM', 'Thorogood 814-4178 Men\'s American Heritage 8\' Moc Toe,  MAXWear Wedge Non-Safety Toe Boot,  Trail Crazyhorse - 8 D(M) US', 194.95, 199.95, 5, 2.5, 'https://www.amazon.com/gp/offer-listing/B01MT163FM/ref=olp_twister_child?ie=UTF8&seller=A27XQSHYXYFFJT&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604cb0066a750013f69570--2020-03-04--19-50-09--est.jpg', '2020-03-05T00:50:13.696Z', true, true, 'New'],
          ['P and R Traders', 'TG-534-6932_6.5-W', '014799826055', 'B002QQ8UDK', 'Thorogood Women\'s Street Athletics Oxford, Black, 6.5 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UDK/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604eb65f7d470021d258d0--2020-03-04--19-58-48--est.jpg', '2019-03-05T00:58:51.372Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_7-W', '014799826062', 'B002QQ8UDU', 'Thorogood Women\'s Street Athletics Oxford, Black, 7 W US', 124.95, 139.95, 15, 10.72, 'https://www.amazon.com/gp/offer-listing/B002QQ8UDU/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6045cf3f0c94002f07f19d--2020-03-04--19-20-45--est.jpg', '2019-03-05T00:20:51.123Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_8-W', '014799826086', 'B002QQ8UEE', 'Thorogood Women\'s Street Athletics Oxford, Black, 8 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UEE/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6045fced486b0021d95fc6--2020-03-04--19-21-33--est.jpg', '2019-03-05T00:21:37.674Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_9.5-W', '014799826116', 'B002QQ8UF8', 'Thorogood Women\'s Street Athletics Oxford, Black, 9.5 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UF8/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60462a066a750013f68d9b--2020-03-04--19-22-20--est.jpg', '2019-03-05T00:22:43.445Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_10-W', '014799826123', 'B002QQ8UFS', 'Thorogood Women\'s Street Athletics Oxford, Black, 10 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UFS/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60466a3f0c94002f07f255--2020-03-04--19-23-11--est.jpg', '2019-03-05T00:23:11.725Z', false, false, 'New'],
          ['P and R Traders', 'TG-534-6932_11-W', '014799826130', 'B002QQ8UG2', 'Thorogood Women\'s Street Athletics Oxford, Black, 11 W US', 134.95, 139.95, 5, 3.57, 'https://www.amazon.com/gp/offer-listing/B002QQ8UG2/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604684ed486b0021d96086--2020-03-04--19-23-54--est.jpg', '2020-03-05T00:24:04.696Z', false, false, 'New'],
          ['P and R Traders', 'TG-804-6111_8-M', '014799749798', 'B001WLKXO4', 'Thorogood 804-6111 Men\'s Soft Streets Series 10\' Pull-on Wellington Safety Toe Boot,  Black - 8 D(M) US', 139.95, 144.95, 5, 3.45, 'https://www.amazon.com/gp/offer-listing/B001WLKXO4/ref=olp_twister_child?ie=UTF8&seller=A3I0FH7630IXB8&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e6046d6650eb50013f9e477--2020-03-04--19-24-59--est.jpg', '2020-03-05T00:24:59.774Z', false, false, 'New'],
          ['Premium Overstock', 'TG-814-3268_11.5-3E', '840777121115', 'B072BB6JBZ', 'Thorogood Men\'s 814-3268 Omni Series 8\' Waterproof,  Non-Safety Toe Boot,  Brown - 11.5 X-Wide (3E)', 205, 214.95, 9.95, 4.63, 'https://www.amazon.com/gp/offer-listing/B072BB6JBZ/ref=olp_twister_child?ie=UTF8&seller=A2BYBTLO5K521Q&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e604c935f7d470021d2566a--2020-03-04--19-49-37--est.jpg', '2020-03-05T00:49:39.218Z', true, true, 'New'],
          ['WhyPayMoreOnline', 'TG-834-6905_7-XW', '014799717551', 'B001WLUIN0', 'Thorogood Men\'s 834-6905 Soft Streets Series Plain Toe Oxford,  Black - 7 XW', 121.46, 129.95, 8.49, 6.53, 'https://www.amazon.com/gp/offer-listing/B001WLUIN0/ref=olp_twister_child?ie=UTF8&seller=AR0ME1YTLYKB&tag=watcher04-20', 'https://storage.googleapis.com/precise/cs/2020/03/05/5e60494a5f7d470021d252bb--2020-03-04--19-36-12--est.jpg', '2020-03-05T00:36:13.877Z', false, false, 'New']
        ].map(r => [ ...r, ...[ Math.random() * 5 + 1, Math.random() * 10, 'override' ] ])
      },
      configColumns: [
        {
          name: 'seller_name',
          cell: {
            format: {
              type: 'text'
            }
          }
        },
        {
          name: 'sku',
          cell: {
            format: {
              type: 'text'
            }
          }
        },
        {
          name: 'upc/ean',
          cell: {
            format: {
              type: 'text'
            }
          }
        },
        {
          name: 'asin',
          cell: {
            format: {
              type: 'text'
            }
          }
        },
        {
          name: 'title',
          cell: {
            format: {
              type: 'text'
            }
          }
        },
        {
          name: 'seller_price',
          cell: {
            format: {
              type: 'text',
              common: {
                prefix: '$'
              }
            }
          }
        },
        {
          name: 'map_price',
          cell: {
            format: {
              type: 'text',
              common: {
                prefix: '$'
              }
            }
          }
        },
        {
          name: 'diff',
          cell: {
            format: {
              type: 'currency'
            }
          }
        },
        {
          name: 'diff_percent',
          cell: {
            format: {
              type: 'text',
              common: {
                suffix: ' %'
              }
            }
          }
        },
        {
          name: 'link',
          cell: {
            format: {
              type: 'link',
              config: {
                text: '{value}'
              }
            }
          }
        },
        {
          name: 'screenshot',
          cell: {
            format: {
              type: 'link'
            }
          }
        },
        {
          name: 'captured_at',
          cell: {
            format: {
              type: 'temporal'
            }
          }
        },
        {
          name: 'fba',
          cell: {
            format: {
              type: 'bool',
              config: {
                positive: {
                  text: 'Yes', // default Yes
                  html: '<span class="d-bool-p">Yes</span>'
                },
                negative: {
                  text: 'No', // default No
                  html: '<span class="d-bool-n">No</span>'
                }
              }
            }
          }
        },
        {
          name: 'prime',
          cell: {
            format: {
              type: 'bool',
              positive: {
                text: 'Yes', // default Yes
                html: '<span class="d-bool-p">Yes</span>'
              },
              negative: {
                text: 'No', // default No
                html: '<span class="d-bool-n">No</span>'
              }
            }
          }
        },
        {
          name: 'condition',
          cell: {
            format: {
              type: 'text'
            }
          }
        },
        {
          name: 'rating',
          cell: {
            format: {
              type: 'stars',
              config: {
                value: {
                  display: true
                }
              }
            }
          }
        },
        {
          name: 'growth_value',
          cell: {
            format: {
              type: 'segments'
            }
          }
        },
        {
          name: 'override',
          displayName: 'Override',
          cell: {
            format: {
              type: 'override',
              config: {
                format: {
                  text: '1'
                }
              }
            },
            aggrFormats: {
              int: {
                type: 'text',
                config: {
                }
              }
            }
          }
        }
      ]
    }
  }
})
