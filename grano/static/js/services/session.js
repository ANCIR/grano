grano.factory('session', ['$http', function($http) {
    var dfd = $http.get('/api/1/sessions');

    return {
        get: dfd.success
    };
}]);
