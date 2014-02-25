grano.factory('core', ['$http', function($http) {
    var appName = $('#appName').html();
    var setTitle = function(name) {
        $('title').html(name + ' - ' + appName);
    };
    
    return {
        appName: appName,
        setTitle: setTitle
    };
}]);
