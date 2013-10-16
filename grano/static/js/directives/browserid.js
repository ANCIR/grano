grano.directive('browserid', ['$window', '$http', function ($window, $http) {
    return {
        restrict: 'A',
        link: function(scope, element, attrs) {
            var gotAssertion = function(assertion) {
                console.log(assertion);
                if (assertion) {
                    var data = 'assertion=' + assertion,
                        req = $http.post('/api/1/browserid/login', data, {
                            headers: {'Content-Type': 'application/x-www-form-urlencoded'}
                        });
                    req.then(function(res, status, xhr) {
                            return $window.location.reload(true);
                        },
                        function(res, status, xhr) {
                            return alert("login failure: " + status);
                        }
                    );
                }
            };

            var logoutCallback = function(event) {
                var req = $http.post('/api/1/browserid/logout');
                req.then(function() {
                        return $window.location.reload(true);
                    },
                    function(res, status, xhr) {
                        console.log(res);
                        return alert("logout failure: " + status);
                    });
                return false;
            };

            element.bind('click', function() {
                if (attrs.browserid==='login') {
                    navigator.id.get(gotAssertion);
                } else {
                    navigator.id.logout(logoutCallback);
                }
                return false;
            });
        }
    };
}]);
