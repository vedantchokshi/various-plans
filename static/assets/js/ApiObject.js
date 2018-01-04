class ApiObject {
    constructor(apiJsonResponse) {
        //Assign values from object returned from API
        Object.assign(this, apiJsonResponse);
    }
}