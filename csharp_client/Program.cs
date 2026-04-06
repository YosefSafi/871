using System;
using System.Net.WebSockets;
using System.Text;
using System.Text.Json;
using System.Threading;
using System.Threading.Tasks;
using Spectre.Console;

namespace RoguelikeClient
{
    class Program
    {
        static async Task Main(string[] args)
        {
            AnsiConsole.MarkupLine("[bold green]Connecting to Labyrinth of Despair...[/]");

            using var ws = new ClientWebSocket();
            try
            {
                await ws.ConnectAsync(new Uri("ws://localhost:8000/ws"), CancellationToken.None);
                AnsiConsole.MarkupLine("[bold green]Connected![/]");
                
                var receiveTask = ReceiveLoop(ws);
                var inputTask = InputLoop(ws);

                await Task.WhenAny(receiveTask, inputTask);
            }
            catch (Exception ex)
            {
                AnsiConsole.MarkupLine($"[bold red]Connection failed: {ex.Message}[/]");
            }
        }

        static async Task ReceiveLoop(ClientWebSocket ws)
        {
            var buffer = new byte[1024 * 64]; // 64KB buffer for large map data
            while (ws.State == WebSocketState.Open)
            {
                var result = await ws.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);
                if (result.MessageType == WebSocketMessageType.Close)
                {
                    AnsiConsole.MarkupLine("[bold red]Server closed connection.[/]");
                    break;
                }

                var jsonStr = Encoding.UTF8.GetString(buffer, 0, result.Count);
                try
                {
                    using var doc = JsonDocument.Parse(jsonStr);
                    RenderGame(doc.RootElement);
                }
                catch (Exception e)
                {
                    // Ignore parse errors from partial reads for now, simple implementation
                }
            }
        }

        static async Task InputLoop(ClientWebSocket ws)
        {
            while (ws.State == WebSocketState.Open)
            {
                if (Console.KeyAvailable)
                {
                    var key = Console.ReadKey(true).Key;
                    int dx = 0, dy = 0;

                    if (key == ConsoleKey.UpArrow || key == ConsoleKey.W) dy = -1;
                    else if (key == ConsoleKey.DownArrow || key == ConsoleKey.S) dy = 1;
                    else if (key == ConsoleKey.LeftArrow || key == ConsoleKey.A) dx = -1;
                    else if (key == ConsoleKey.RightArrow || key == ConsoleKey.D) dx = 1;

                    if (dx != 0 || dy != 0)
                    {
                        var payload = $"{{\"action\":\"move\",\"dir\":[{dx},{dy}]}}";
                        var bytes = Encoding.UTF8.GetBytes(payload);
                        await ws.SendAsync(new ArraySegment<byte>(bytes), WebSocketMessageType.Text, true, CancellationToken.None);
                    }
                }
                await Task.Delay(10); // Prevent CPU thrashing
            }
        }

        static void RenderGame(JsonElement state)
        {
            int width = state.GetProperty("width").GetInt32();
            int height = state.GetProperty("height").GetInt32();
            var map = state.GetProperty("map");
            var player = state.GetProperty("player");
            var enemies = state.GetProperty("enemies");
            var logs = state.GetProperty("logs");

            // Build grid
            var canvas = new Canvas(width, height);

            // Draw map
            for (int x = 0; x < width; x++)
            {
                for (int y = 0; y < height; y++)
                {
                    int tile = map[x][y].GetInt32();
                    if (tile == 1) // Wall
                    {
                        canvas.SetPixel(x, y, Color.Grey);
                    }
                    else
                    {
                        canvas.SetPixel(x, y, Color.Black); // Floor
                    }
                }
            }

            // Draw enemies
            foreach (var enemy in enemies.EnumerateArray())
            {
                int ex = enemy.GetProperty("x").GetInt32();
                int ey = enemy.GetProperty("y").GetInt32();
                canvas.SetPixel(ex, ey, Color.Red);
            }

            // Draw player
            int px = player.GetProperty("x").GetInt32();
            int py = player.GetProperty("y").GetInt32();
            int hp = player.GetProperty("hp").GetInt32();
            canvas.SetPixel(px, py, Color.Green);

            // Build Layout
            var layout = new Layout("Root")
                .SplitRows(
                    new Layout("Top").SplitColumns(
                        new Layout("Game", new Panel(canvas).Expand().Header("Labyrinth")),
                        new Layout("Stats", new Panel(new Markup($"[green]Player HP: {hp}[/]")).Expand().Header("Stats"))
                    ),
                    new Layout("Logs", new Panel(BuildLogs(logs)).Expand().Header("Action Log"))
                );

            layout["Top"].Ratio(7);
            layout["Game"].Ratio(7);
            layout["Stats"].Ratio(3);
            layout["Logs"].Ratio(3);

            AnsiConsole.Clear();
            AnsiConsole.Write(layout);
        }

        static Markup BuildLogs(JsonElement logs)
        {
            var sb = new StringBuilder();
            foreach (var log in logs.EnumerateArray())
            {
                sb.AppendLine($"[yellow]- {log.GetString()}[/]");
            }
            return new Markup(sb.ToString());
        }
    }
}
