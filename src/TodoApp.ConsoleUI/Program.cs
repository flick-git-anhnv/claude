using Microsoft.Extensions.DependencyInjection;
using TodoApp.Application;
using TodoApp.ConsoleUI;
using TodoApp.Domain;
using TodoApp.Infrastructure;

// UTF-8 để hiển thị tiếng Việt và ký tự Unicode (DESIGN §12.1)
Console.OutputEncoding = System.Text.Encoding.UTF8;

var services = new ServiceCollection();
services.AddSingleton<JsonStorageOptions>();
services.AddSingleton<ITodoRepository, JsonFileRepository>();
services.AddSingleton<ITodoService, TodoService>();
services.AddSingleton<AppRunner>();

var provider = services.BuildServiceProvider();

var runner = provider.GetRequiredService<AppRunner>();
runner.Run();
