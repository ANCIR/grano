
grano.handleFormError = function(form) {
  return function(data, status) {
    if (status == 400) {
        var errors = [];
        for (var field in data.errors) {
            form[field].$setValidity('value', false);
            form[field].$message = data.errors[field];
            errors.push(field);
        }
        if (angular.isDefined(form._errors)) {
            angular.forEach(form._errors, function(field) {
                if (errors.indexOf(field) == -1) {
                    form[field].$setValidity('value', true);
                }
            });
        }
        form._errors = errors;
    } else {
      // TODO: where is your god now?
      if (angular.isObject(data) && data.message) {
        alert(data.message);
      }
      //console.log(status, data);
    }
  };
};
