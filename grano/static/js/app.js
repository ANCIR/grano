var grano = angular.module('grano', [], function($routeProvider, $locationProvider) {
  $routeProvider.when('/', {
    templateUrl: '/static/templates/home.html',
    controller: HomeCtrl
  });

  $routeProvider.otherwise({
    redirectTo: '/'
  });

  $locationProvider.html5Mode(true);
});