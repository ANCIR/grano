function AppCtrl($scope, $window, $routeParams, $location, $modal, session, core) {
    $scope.session = {logged_in: false};
    core.setTitle('Welcome');

    session.get(function(data) {
        $scope.session = data;
    });

    $scope.showAccount = function() {
        var d = $modal.open({
            templateUrl: '/static/templates/account.html',
            controller: 'AccountCtrl'
        });
    };
}

AppCtrl.$inject = ['$scope', '$window', '$routeParams', '$location', '$modal', 'session', 'core'];
