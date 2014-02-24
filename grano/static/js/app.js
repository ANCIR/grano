var grano = angular.module('grano', ['ngRoute']);

grano.config(['$routeProvider', '$locationProvider', '$sceProvider',
    function($routeProvider, $locationProvider, $sceProvider) {

  $routeProvider.when('/', {
    templateUrl: '/static/templates/home.html',
    //controller: HomeCtrl
  });

  $routeProvider.otherwise({
    redirectTo: '/' //visitPath
  });

  $locationProvider.html5Mode(false);
  //$sceProvider.enabled(false);
}]);
