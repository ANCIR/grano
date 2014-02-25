function AppCtrl($scope, $window, $routeParams, $location, session, core) {
    $scope.session = {logged_in: false};
    core.setTitle('Welcome');

    session.get(function(data) {
        $scope.session = data;
    });
}

AppCtrl.$inject = ['$scope', '$window', '$routeParams', '$location', 'session', 'core'];
