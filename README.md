beta-search-api
=================
Service to allow api customers to search for course resources.

Builds

master - [![Build Status](https://dev.azure.com/ofsbeta/discoverUni/_apis/build/status/prod/prod-search-api?branchName=master)](https://dev.azure.com/ofsbeta/discoverUni/_build/latest?definitionId=17&branchName=master)

develop - [![Build Status](https://dev.azure.com/ofsbeta/discoverUni/_apis/build/status/dev/dev-search-api?branchName=develop)](https://dev.azure.com/ofsbeta/discoverUni/_build/latest?definitionId=31&branchName=develop)


### Configuration Settings

Add the following to your local.settings.json:

| Variable                         | Default                | Description                                                                                                                                                                                     |
|----------------------------------|------------------------|-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| FUNCTIONS_WORKER_RUNTIME         | python                 | The programming language the function worker runs on                                                                                                                                            |
| AzureCosmosDbUri                 | {retrieve from portal} | The uri to the cosmosdb instance                                                                                                                                                                |
| AzureCosmosDbKey                 | {retrieve from portal} | The database key to access cosmosdb instance                                                                                                                                                    |
| AzureCosmosDbDatabaseId          | discoveruni            | The database where documents are stored                                                                                                                                                         |
| AzureCosmosDbDataSetCollectionId | datasets               | The name of the collection in which datasets are loaded                                                                                                                                         |
| AzureWebJobsStorage              | {retrieve from portal} | The default endpoint to access storage account                                                                                                                                                  |
| StopEtlPipelineOnWarning         | false                  | Boolean flag to stop function worker on a warning                                                                                                                                               |
| PostcodeIndexName                | postcodes              | The storage container that will trigger the function                                                                                                                                            |
| SearchURL                        | {retrieve from portal} | The uri to the azure search instance                                                                                                                                                            |
| SearchAPIKey                     | {retrieve from portal} | The api key to access the azure search instance                                                                                                                                                 |
| AzureSearchAPIVersion            | 2019-05-06             | The azure search API version for instance                                                                                                                                                       |
| HardcodedHighestDataset          | 0                      | The highest dataset that will be loaded into the search index. This is used to determine which dataset to load into the search index. NB zero means use internal method not the hardcoded value |

### Setup

### Pre-Setup

1) Install [.Net Core 2.2 SDK](https://dotnet.microsoft.com/download), if you haven't already.
2) Install python 3.6.8 - the latest stable version that works with Azure client.
```
Mac user:
Install homebrew:
1) /usr/bin/ruby -e "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install)"
2) brew install sashkab/python/python36
3) pip3.6 install -U pip setuptools

Windows user:
```
3) Make sure Python 3.6.8 is set on your PATH, you can check this by running `python3 -v` in terminal window.
4) Install Azure Client
```
Mac user:
brew tap azure/functions
brew install azure-functions-core-tools

Windows user:
```
5) Setup Visual Studio Code, install [visual studio code](https://code.visualstudio.com/)
6) Also install the following extensions for visual studio code - documentation [here](https://code.visualstudio.com/docs/editor/extension-gallery)

```
Python
Azure CLI Tools
Azure Account
Azure Functions
Azure Storage
```

7) Sign into Azure with Visual Studio Code - follow documentation [here](https://docs.microsoft.com/en-us/azure/azure-functions/tutorial-vs-code-serverless-python#_sign-in-to-azure)

#### Building resources and running azure function locally

1) Requires [beta-data-pipelines](https://github.com/office-for-students/beta-data-pipelines) to have been built and run once to load data into search index as well as the [beta-postcode-builder](https://github.com/office-for-students/beta-postcode-builder)

2) Retrieve SearchURL and SearchAPIKey from azure search instance that your search API will be connecting to.

3) Retrieve the Azure Storage conection string from azure storage container instance.

3) Create your local.settings.json file at root level of repository and include all environment variables in the configuration settings table above.

6) Create a virtual machine to run the azure function application by running `venv .env` at root level of repository.

7) Run service on virtual machine by doing the following:
```
source .env/bin/activate
pip install -r requirements.txt
func host start
```

### Tests

To run tests, run the following command: `pytest -v`

### Contributing

See [CONTRIBUTING](CONTRIBUTING.md) for details.

### License

See [LICENSE](LICENSE.md) for details.
