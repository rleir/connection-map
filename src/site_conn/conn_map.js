'use strict';

document.addEventListener("DOMContentLoaded", function(event) { 
    var formButton = L.DomUtil.get("a-button");
    var formSelect = document.getElementById("year-select");

    formButton.addEventListener("click", function(event){
        event.preventDefault()
    });

    var map = L.map('map').setView([30.5, -0.09], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

    const MAX_DECADE = 2030;
    const MIN_DECADE = 1960;  // this can be older when paper records have been transcribed

    // Create panes for the decades
    // array of n panes -- one per decade from min decade to max decade
    let panes = [];
    let n_panes = (MAX_DECADE - MIN_DECADE)/10 + 1;
    for( let pane_index = 0; pane_index< n_panes; pane_index++) {
        // append new pane to the array
        panes.push( map.createPane('pane'+pane_index));
    }

    // add options to the selector for all decades
    for (let decade = MIN_DECADE; decade<=MAX_DECADE; decade += 10){
        let opt = document.createElement('option');
        let decade_str = "" + decade;
        opt.value = decade_str;
        opt.innerHTML = decade_str;
        formSelect.appendChild(opt);
    }

    formButton.onclick = function() {
        let decade_str = formSelect.options[ formSelect.selectedIndex].text;
        let decade = Number(decade_str)

        if( decade >= MAX_DECADE) {
            decade = MIN_DECADE;
        } else {
            decade += 10;
        }
        // update the selector
        formSelect.value = "" + decade;

        revealData(decade);
    }

    formSelect.onchange = function() {
        let decade = this.value;
        revealData(decade);
    }

    function hide(index) {
        // hide the markers
        panes[index].style.display = 'none';
    }

    function polyDel(){
        for(let i in map._layers) {
            if(map._layers[i]._path != undefined) {
                try {
                    map.removeLayer(map._layers[i]);
                }
                catch(e) {
                    console.log("problem with " + e + map._layers[i]);
                }
            }
        }
    }

    function show(index) {
        // show the markers
        panes[index].style.display = '';
        // create polylines
        polyWrite(index);
    }

    function polyWrite(index){
        let decade_range = year_ranges[index];

        L.geoJSON([decade_range], {

            style: function (feature) {
                return feature.properties && feature.properties.style;
            },

            pointToLayer: function (feature, latlng) {
                let colors = ['#865f00', '#d10068', '#b42f54'];
                let dashArrays= [ "4, 1", "2, 1", "8, 1"];

                let outloan = false;
                let  inloan = false;
                if( feature.properties.popupContent) {
                    for(let key in feature.properties.popupContent) {
                        let loansdir = key.substr(0,1);
                        if( loansdir == 'O'){
                            outloan = true;
                        }
                        else if( loansdir == 'I'){
                            inloan = true;
                        }
                    }
                }
                // just  inloan 0
                // just outloan 1
                // both in and out 2
                // neither: assumed not possible
                let colorx = 0;
                if(outloan){
                    colorx++;
                    if(inloan) {
                        colorx++;
                    }
                }
                // using Henry Thasler's library
                // https://www.thasler.com/leaflet.geodesic/example/interactive-noWrap.html
                // an arc from ottawa to latlng
                return L.geodesic([[[45.421, -75.697], latlng]], {
                    weight: 2 * feature.properties.mag,
                    opacity: 0.5,
                    color: colors[colorx],
                    dashArray: dashArrays[colorx],
                    dashOffset: "1",
                    steps: 50,
                    wrap: false
                });
            }
        }).addTo(map);
    }

    function revealData(decade){
        // delete the polylines
        polyDel();

        // decade to index
        let new_p_index = (decade - MIN_DECADE)/10;
        if(new_p_index <0) {
            console.log("error new_pane_index " + new_p_index);
        }
        // hide all old marker panes
        panes.forEach( function(value, index, array) {
            if(index != new_p_index) {
                hide( index);
            }
        });
        // show new pane
        show(new_p_index);
    }

    // create popup tooltip info for each marker
    // showing city name, years and institutons
    function onEachFeature(feature, layer) {
        let popupContent = "";
        let outloanInsts = [];
        let outloanNum = [];
        let inloanInsts = [];
        let inloanNum = [];
        if (feature.properties) {
            if( feature.properties.place) {
                popupContent += feature.properties.place;
                popupContent += "<br>";
                popupContent += "years= "
                if( ! feature.properties.years){
                    console.log("no years " + feature.properties.place);
                } else {
                    feature.properties.years.forEach( function(value, index, array) {
                        popupContent += value + ", ";
                    });
                }
                popupContent += "<br>";
            }
            if( feature.properties.popupContent) {
                for(let key in feature.properties.popupContent) {
                    let loansdir = key.substr(0,1);
                    let instname = key.substr(1);
                    let quantity = feature.properties.popupContent[key];
                    if( loansdir == 'O'){
                        outloanInsts.push(instname);
                        outloanNum.push(quantity);
                    }
                    if( loansdir == 'I'){
                        inloanInsts.push(instname);
                        inloanNum.push(quantity);
                    }
                }
                if( outloanInsts.length > 0){
                    popupContent += "Loans Out:";
                    popupContent += "<br>";
                    popupContent += "<ul>";
                    outloanInsts.forEach(function(value, index, array) {
                        popupContent += "<li>";
                        popupContent += outloanNum[index];
                        popupContent += " - ";
                        popupContent += value;
                        popupContent += "</li>";
                    });
                    popupContent += "</ul>";
                }
                if( inloanInsts.length > 0){
                    popupContent += "Loans In:";
                    popupContent += "<br>";
                    popupContent += "<ul>";
                    inloanInsts.forEach(function(value, index, array) {
                        popupContent += "<li>";
                        popupContent += inloanNum[index];
                        popupContent += " - ";
                        popupContent += value;
                        popupContent += "</li>";
                    });
                    popupContent += "</ul>";
                }
            }
        }
        layer.bindTooltip(popupContent); // or bindPopup
    }

    // get the input features in a decade,
    //   and create a feature per address which aggregates input features
    //   for all years in the decade
    function build_decade_range (pane_index){
        let decade_features = {}  // accumulate the results in this

        // the date range
        let decade_start = pane_index * 10 + MIN_DECADE;
        let decade_end = decade_start + 10;

        // scan the input features, looking for ones which are within the decade
        //  TODO: scan once, not many times
        connData.features.forEach( function(feature, index, array) {
            let year = feature.properties.year;
            if(year >= decade_start &&
               year < decade_end ){
                let addr = feature.properties.place;
                // is this in  decade_features? create or deep merge
                //if(!(addr in Object.keys(decade_features))) {
                if(!(addr in decade_features)) {
                    decade_features[addr] = {"type": "Feature"};
                    decade_features[addr]["properties"] = Object.assign(feature.properties);
                    decade_features[addr].properties["years"] = [feature.properties.year];
                    decade_features[addr]["geometry"] = feature.geometry;
                } else {
                    let props = decade_features[addr]["properties"];
                    props.years.push(feature.properties.year);

                    for( let inst in feature.properties.popupContent){
                        // is this inst in decade_features? create or sum
                        if( !(inst in props.popupContent)){
                            props.popupContent[inst] = 0;
                        }
                        props.popupContent[inst] += feature.properties.popupContent[inst];
                    }
                }
            }
        });

        let decade_range = {
            "type": "FeatureCollection",
            "metadata": {},
            "features": []
        };
        decade_range.metadata = connData.metadata;

        // decade_features.forEach( function(feature, index, array) {
        for( let dec_feature in decade_features){
            decade_range.features.push(decade_features[dec_feature]);
        }
        return decade_range;
    }

    // disable the shadow
    let icon = new L.Icon.Default();
    icon.options.shadowSize = [0,0];

    // group the input features by address,decade
    let year_ranges = [];
    year_ranges.metadata = connData.metadata;

    for( let pane_index = 0; pane_index< n_panes; pane_index++) {
        // start off with hidden markers
        panes[pane_index].style.display = 'none';

        let decade_range = build_decade_range (pane_index);
        // append new pane to the array
        year_ranges.push( decade_range );

        L.geoJSON([decade_range], {

            style: function (feature) {
                return feature.properties && feature.properties.style;
            },

            onEachFeature: onEachFeature,

            pointToLayer: function (feature, latlng) {
                let p_index = Math.floor((feature.properties.year - MIN_DECADE)/10);  // zzz check for float/int problems
                if(p_index <0) {
                    console.log("error p_index " + p_index);
                }
                let pane = panes[p_index];
                return L.marker(latlng, {
                    icon: icon,
                    pane: panes[p_index]
                });
            }
        }).addTo(map);
    }

    // the initial load
    revealData(formSelect.options[ formSelect.selectedIndex].text);
});

