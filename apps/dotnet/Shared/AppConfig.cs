namespace AzureFunctionsGuide.Shared;

/// <summary>
/// Centralized application configuration from environment variables.
/// </summary>
public static class AppConfig
{
    public static string AppName => System.Environment.GetEnvironmentVariable("APP_NAME") ?? "azure-functions-dotnet-guide";
    public static string Version => "1.0.0";
    public static string FunctionAppName => System.Environment.GetEnvironmentVariable("WEBSITE_SITE_NAME") ?? "local";
    public static string FunctionsEnvironment => System.Environment.GetEnvironmentVariable("AZURE_FUNCTIONS_ENVIRONMENT") ?? "production";
}
