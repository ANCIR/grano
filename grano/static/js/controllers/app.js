function AppCtrl($scope, $window, $routeParams, $location, session) {
    session.get(function(data) {
        $scope.session = data;
    });

    /*
    $scope.$on("$routeChangeStart", function (event, next, current) {
        if (next && next.$$route.accessPolicy==='user') {
            identity.checkSession(function(data) {
                $location.path('/');
                alertService.flash('error', 'Sorry, you need to be logged in to view this page.');
            });
        }
    });*/
}

AppCtrl.$inject = ['$scope', '$window', '$routeParams', '$location', 'session'];