
function ProjectsViewCtrl($scope, $routeParams, $location, $http, $modal, $timeout, session) {
    $scope.project = {};
    
    $http.get('/api/1/projects/' + $routeParams.slug).then(function(res) {
        $scope.project = res.data;
    });
}

ProjectsViewCtrl.$inject = ['$scope', '$routeParams', '$location', '$http', '$modal', '$timeout', 'session'];
