var grano = angular.module('grano', ['ngRoute', 'ui.bootstrap']);

grano.config(['$routeProvider', '$locationProvider',
    function($routeProvider, $locationProvider) {

  $routeProvider.when('/', {
    templateUrl: '/static/templates/home.html',
    controller: HomeCtrl
  });

  $routeProvider.when('/p/:slug', {
    templateUrl: '/static/templates/projects/view.html',
    controller: ProjectsViewCtrl
  });

  $routeProvider.otherwise({
    redirectTo: '/'
  });

  $locationProvider.html5Mode(false);
}]);
