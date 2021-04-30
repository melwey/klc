// KLC: Copernicus global land cover 2015-2019
// for each year (2015:2019)
// for each geometry (KLC)
// for each cover type bands[2:11]("bare-coverfraction", "urban-coverfraction", "crops-coverfraction", 
// "grass-coverfraction", "moss-coverfraction", "water-permanent-coverfraction", "water-seasonal-coverfraction",
// "shrub-coverfraction", "snow-coverfraction", "tree-coverfraction")

// imort data
var lc = ee.ImageCollection("COPERNICUS/Landcover/100m/Proba-V-C3/Global"),
    lc2019 = ee.Image("COPERNICUS/Landcover/100m/Proba-V-C3/Global/2019"),
    klc = ee.FeatureCollection("users/mweynants/BIOPAMA/klc_2020"),
    wdpa = ee.FeatureCollection("WCMC/WDPA/current/polygons");

// set KLC
var klclist = klc
  // list of features
  .toList(100) 
  // list of KLC_ID
  .map(function(f){return ee.Feature(f).get("KLC_ID");})
//   // test on a subset
//   .filter(ee.Filter.inList("item", ['WAF_21', 'CAF_08']));
// print(klclist);

// set years
var years = ee.List.sequence(2015,2019);
// // test on a subset
// years = years.filter(ee.Filter.gt("item", 2017));
// print(years);

var myfun = function(klcid){
  // set feature
  var feature = klc.filter(ee.Filter.equals("KLC_ID", klcid));
  // function running on years
  var getCover = function(year){
    
    // filter wdpa
    // Define a collection with geometries from wdpa that intersect feature.
    var clip = function(pa){
      if (pa){
        var r = wdpa.filter(ee.Filter.equals("PA_DEF", '1')).filterBounds(feature.geometry());
      } else {
        var r = ee.FeatureCollection(feature.geometry());
      }
      return r;
    }; // end clip
    
    // get image
    var inputImage = lc
      // get year
      .filterDate(ee.Date.fromYMD(year, 1, 1), ee.Date.fromYMD(year, 12,31))
      .first()
      // select bands 
      .select(ee.List.sequence(2,11))
      // clip to wdpa
      .clipToCollection(clip(pa));
    
    // compute area
    var value = inputImage
      // multiply pixels by area in sqkm, divide by 100 (%)
      .multiply(ee.Image.pixelArea().divide(1000 * 1000 * 100))
      // sum area
      .reduceRegion({
            reducer: ee.Reducer.sum(),
            geometry: feature.geometry(),
            scale: 100,
            maxPixels: 1e13
          });
          
    // output
    return (
      ee.Dictionary(value)
        .set('Year', year)
        .set('PA',pa)
        .set('KLC_ID', klcid)
        );
  }; // end getCover
  
// map function on years
// total
var pa = false; 
var tmp = years.map(getCover);
// inside pa
pa = true;
tmp = tmp.cat(years.map(getCover)); 

// output
return tmp; // list
}; // end myfun

var myresults = klclist.map(myfun)
  // flatten list
  .flatten()
  // transform as list of features for export
  .map(function(d) {return ee.Feature(null).set(d);});
// print(myresults);

// export
Export.table.toDrive({
    collection: ee.FeatureCollection(myresults),
    description: 'CGLCstats_KLC',
    fileFormat: 'CSV'
    });