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
    var panes = [];
    let n_panes = (MAX_DECADE - MIN_DECADE)/10 + 1;
    for( var pane_index = 0; pane_index< n_panes; pane_index++) {
        // append new pane to the array
        panes.push( map.createPane('pane'+pane_index));
    }

    // add options to the selector for all decades
    for (var decade = MIN_DECADE; decade<=MAX_DECADE; decade += 10){
        var opt = document.createElement('option');
        var decade_str = "" + decade;
        opt.value = decade_str;
        opt.innerHTML = decade_str;
        formSelect.appendChild(opt);
    }

    formButton.onclick = function() {
        //      zzz  let decade_str = formSelect.node().value;
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
        var decade = this.value;
        revealData(decade);
    }
    // the initial load
    revealData(formSelect.options[ formSelect.selectedIndex].text);

    function hide(index) {
        panes[index].style.display = 'none';
    }
    function show(index) {
        panes[index].style.display = '';
    }
    function revealData(decade){
        // decade to index
        var new_p_index = (decade - MIN_DECADE)/10;
        if(new_p_index <0) {
            console.log("zzz pane_index " + new_p_index);
        }
        // hide all old panes
        panes.forEach( function(value, index, array) {
            if(index != new_p_index) {
                hide( index);
            }
        });
        // show new pane
        show(new_p_index);
    }

    function onEachFeature(feature, layer) {
        var popupContent = "";
        var outloanInsts = [];
        var outloanNum = [];
        var inloanInsts = [];
        var inloanNum = [];
        if (feature.properties) {
            if( feature.properties.place) {
                popupContent += feature.properties.place;
                popupContent += "<br>";
            }
            // zzz insti names in data
            if( feature.properties.popupContent) {
                for(var key in feature.properties.popupContent) {
                    var loansdir = key.substr(0,1);
                    var instname = key.substr(1);
                    if( loansdir == 'O'){
                        outloanInsts.push(instname);
                        outloanNum.push(feature.properties.popupContent[key]);
                    }
                    if( loansdir == 'I'){
                        inloanInsts.push(instname);
                        inloanNum.push(feature.properties.popupContent[key]);
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

    // disable the shadow
    var icon = new L.Icon.Default();
    icon.options.shadowSize = [0,0];

    L.geoJSON([connData], {

        style: function (feature) {
            // feature.properties.mag    zzzz
            return feature.properties && feature.properties.style;
        },

        onEachFeature: onEachFeature,

        pointToLayer: function (feature, latlng) {
            var p_index = Math.floor((feature.properties.year - MIN_DECADE)/10);  // zzz check for float/int problems
            var pane = panes[p_index];

            if(p_index <0) {
                console.log("zzz pane_index " + p_index);
            }

            // using Henry Thasler's library
            // https://www.thasler.com/leaflet.geodesic/example/interactive-noWrap.html
            // an arc from ottawa to latlng
            L.geodesic([[[45.421, -75.697], latlng]], {
                weight: 2,
                opacity: 0.5,
                color: 'blue',
                steps: 50,
                pane: pane,
                wrap: false
            }).addTo(map);

            return L.marker(latlng, {
                icon: icon,
                pane
            });
        }
    }).addTo(map);

});

