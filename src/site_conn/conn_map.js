document.addEventListener("DOMContentLoaded", function(event) { 

    var map = L.map('map').setView([30.5, -0.09], 2);

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
    }).addTo(map);

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
                    loansdir = key.substr(0,1);
                    instname = key.substr(1);
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

    L.geoJSON([connData], {

        style: function (feature) {
            // feature.properties.mag    zzzz
            return feature.properties && feature.properties.style;
        },

        onEachFeature: onEachFeature,

        pointToLayer: function (feature, latlng) {

            // using Henry Thasler's library
            // https://www.thasler.com/leaflet.geodesic/example/interactive-noWrap.html

            //var B = L.marker(Kalaeloa_Airport, {draggable: true}).addTo(map).bindPopup("Drag me.").openPopup();
            // an arc from ottawa to latlng
            L.geodesic([[[45.421, -75.697], latlng]], {
                weight: 2,
                opacity: 0.5,
                color: 'blue',
                steps: 50,
                wrap: false
            }).addTo(map);

            return L.marker(latlng);
        }
    }).addTo(map);

});

