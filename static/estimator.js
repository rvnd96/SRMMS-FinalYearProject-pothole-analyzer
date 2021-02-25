(function () {

  'use strict';

  var app = angular.module('MyApp', [])

  .controller('SearchController', ['$scope', '$http', '$filter',
    function($scope, $http, $filter) {
		
		$scope.url = window.location.origin;

		$scope.grades = [15,20,25,30,35,40];
		$scope.workers = [];
		$scope.selectedWorkers = function(){
			return $scope.workers.filter(w=>w.count > 0);
		};

		$scope.selectedManDays = function(){
			var actualManDays = $scope.result.days;
			var pool = $scope.selectedWorkers();
			var dailyActualWork = pool.map(x=>x.ratio*x.count).reduce(function(total, num) {
				return total + num;
			},0);
			if(dailyActualWork == 0){
				dailyActualWork = 1;
			}
			return Math.ceil(actualManDays/dailyActualWork);
		}

		$scope.selectedMonth = new Date();
		$scope.selectedGrade = $scope.grades[0];

		$scope.settings = {
			l: 0,
			w: 0,
			d: 0.10
		}

		$scope.volume = function(){
			return $scope.settings.l * $scope.settings.w * $scope.settings.d
		}

		$scope.result = {
			material: 0,
			other: 0,
			days: 0
		}

		// $scope.result = {
		// 	"material": 169856.666461037,
		// 	"other": 64154.6080956697,
		// 	"days": 12
		// }

		$scope.workerCost = function(){
			if($scope.selectedWorkers().length == 0){
				return 0;
			}
			return $scope.selectedManDays() * $scope.selectedWorkers().map(x=>x.rate*x.count).reduce(function(total, num) {
				return total + num;
			},0);
		}

		$scope.totalCost = function(){
			return $scope.result.material + $scope.result.other + $scope.workerCost()
		}
		
		$scope.apiCallInProgress = false;
		
		$scope.getValues = function(date,grade,volume){
			$scope.apiCallInProgress = true;
			$http.post($scope.url + '/predictCosts', {
				year: parseInt($filter('date')(date, 'yyyy')),
				month: parseInt($filter('date')(date, 'MM')),
				grade: grade,
				volume: volume
			}, {
				headers: {
					'Content-Type': 'application/json'
				}
			}).success(function (data) {
				$scope.result = data;
				$scope.apiCallInProgress = false;
			}).error(function(data){
				$scope.apiCallInProgress = false;
			});
		}

		
		$http.get($scope.url + '/workers').success(function (data) {
			$scope.workers = data;
		}).error(function(data){
			alert("Error Loading Workers");
		});
  }

  ]);
  
  app.config(function($interpolateProvider,$compileProvider) {
    $interpolateProvider.startSymbol('[[');
    $interpolateProvider.endSymbol(']]');
	$compileProvider.aHrefSanitizationWhitelist(/^\s*(https?|mailto|sms|tel|ciscotel|sip|CISCOTEL|SIP):/);
  });

  app.filter("trustUrl", ['$sce', function ($sce) {
	return function (recordingUrl) {
		return $sce.trustAsResourceUrl(recordingUrl);
	};
  }]);

}());