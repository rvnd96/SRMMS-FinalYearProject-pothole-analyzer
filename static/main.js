(function () {

  'use strict';

 
/**
 * Captures a image frame from the provided video element.
 *
 * @param {Video} video HTML5 video element from where the image frame will be captured.
 * @param {Number} scaleFactor Factor to scale the canvas element that will be return. This is an optional parameter.
 *
 * @return {Canvas}
 */
function capture(video, scaleFactor) {
    if(scaleFactor == null){
        scaleFactor = 1;
    }
    var w = video.videoWidth * scaleFactor;
    var h = video.videoHeight * scaleFactor;
    var canvas = document.createElement('canvas');
        canvas.width  = w;
        canvas.height = h;
    var ctx = canvas.getContext('2d');
        ctx.drawImage(video, 0, 0, w, h);
    return canvas;
} 

  var app = angular.module('MyApp', [])

  .controller('SearchController', ['$scope', '$http',
    function($scope, $http) {
		
		$scope.url = window.location.origin;

		$scope.videos = [];

		$scope.settings = {
			dMin: 5,
			dMax: 100,
			degreeOfView: 120
		}

		$scope.shoot = function(){
			var video  = document.getElementById('player');
			var canvas = capture(video, 1);
			return canvas.toDataURL();
		}
		
		$scope.isDetecting = false;
		$scope.result = {
			ErrorMessage: null,
			HasError: false,
			Results: null
		};

		// $scope.result = {
		// 	"rois": [
		// 		[
		// 			702,
		// 			1378,
		// 			831,
		// 			1692
		// 		],
		// 		[
		// 			873,
		// 			1394,
		// 			1027,
		// 			1621
		// 		],
		// 		[
		// 			404,
		// 			55,
		// 			960,
		// 			1071
		// 		],
		// 		[
		// 			476,
		// 			1258,
		// 			555,
		// 			1396
		// 		],
		// 		[
		// 			581,
		// 			1417,
		// 			713,
		// 			1852
		// 		]
		// 	],
		// 	"class_ids": [
		// 		1,
		// 		1,
		// 		1,
		// 		1,
		// 		1
		// 	],
		// 	"scores": [
		// 		0.9601830840110779,
		// 		0.9576715230941772,
		// 		0.917512834072113,
		// 		0.895280122756958,
		// 		0.8690337538719177
		// 	],
		// 	"size": [
		// 		1920,
		// 		1080
		// 	]
		// };

		$scope.calculator = function(roi){
			window.open('/estimate/'+roi.width.toFixed(2)+'/'+roi.height.toFixed(2));
		}

		$scope.real = function(roi){
			// y1, x1, y2, x2 = roi, https://www.omnicalculator.com/math/right-triangle-side-angle#how-to-find-the-sides-of-a-right-triangle
			var top_pixelHeightFromBottom = $scope.result.size[1] - roi[0];
			var bottom_pixelHeightFromBottom = $scope.result.size[1] - roi[2];

			var bottomDistance = ($scope.settings.dMax - $scope.settings.dMin) * (bottom_pixelHeightFromBottom / $scope.result.size[1]);
			var topDistance = ($scope.settings.dMax - $scope.settings.dMin) * (top_pixelHeightFromBottom / $scope.result.size[1]);

			var bottomWidthPx = $scope.width(roi);
			var bottomFullWidth = $scope.result.size[0];
			
			var alpha = $scope.settings.degreeOfView / 2;
			var beta = 90 - alpha;
			
			var bottomActualHalfWidth = bottomDistance * Math.tan(alpha * Math.PI / 180);
			var bottomActualFullWidth = bottomActualHalfWidth * 2;

			var bottomWidthMeters = bottomWidthPx * bottomActualFullWidth / bottomFullWidth;
			
			return {
				width: bottomWidthMeters,
				height: Math.abs(bottomDistance-topDistance),
				area: bottomWidthMeters * Math.abs(bottomDistance-topDistance)
			};
		};

		$scope.width = function(roi){
			return Math.abs(roi[1] - roi[3]);
		}

		$scope.height = function(roi){
			return Math.abs(roi[0] - roi[2]);
		}

		$scope.area = function(roi){
			return $scope.height(roi) * $scope.width(roi);
		}
		
		$scope.detect = function(){


			var encoded = $scope.shoot();

			if(encoded.length < 7){
				alert("No Video!");
				return;
			}

			//$('#image').attr('src',encoded);

			
			$scope.isDetecting = true;
			$http.post($scope.url + '/detect', {
				image: encoded
			}, {
				headers: {
					'Content-Type': 'application/json'
				}
			}).success(function (data) {
				$scope.result = data;
				$scope.isDetecting = false;
				if(data.HasError){
					$scope.result.Results = null;
				}else{
					$('#image').attr('src', 'data:image/jpeg;base64,' + data.image);
				}
			}).error(function(data){
				$scope.result = {
					ErrorMessage: data.error,
					HasError: true,
					Results: null
				};
				$scope.isDetecting = false;
			});
		}

		$scope.getSelectedVideo = function(){
			return 'static/uploads/' + $scope.selectedVideo;
		}
		
		$http.get($scope.url + '/videos').success(function (data) {
			$scope.videos = data;
			if($scope.videos.length){
				$scope.selectedVideo = $scope.videos[0];
				$scope.loadVideo();
			}
		}).error(function(data){
			alert("Error Loading Videos");
		});

		$scope.loadVideo = function(){
			document.getElementById("player").load();
		}
  }

  ]);
  
  app.config(function($interpolateProvider,$compileProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
  });

  app.filter("trustUrl", ['$sce', function ($sce) {
	return function (recordingUrl) {
		return $sce.trustAsResourceUrl(recordingUrl);
	};
  }]);

}());