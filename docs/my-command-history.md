## 20251224

bash copy:


```
test@MSI:~/leverage-opus$ npx task-master init
  _____         _      __  __           _            
 |_   _|_ _ ___| | __ |  \/  | __ _ ___| |_ ___ _ __ 
   | |/ _` / __| |/ / | |\/| |/ _` / __| __/ _ \ '__|
   | | (_| \__ \   <  | |  | | (_| \__ \ ||  __/ |   
   |_|\__,_|___/_|\_\ |_|  |_|\__,_|___/\__\___|_|   
                                                     
by x.com/eyaltoledano
Taskmaster for teams: tryhamster.com

You need a plan before you execute.

✔ How do you want to build it?
 Together (Hamster)
→ Starting authentication flow...

🔐 Authentication Required

  Selecting cloud storage will open your browser for authentication.
  This enables sync across devices with Hamster.


[auth] Browser Authentication

  Opening your browser to authenticate...
  If the browser doesn't open, visit:
  https://tryhamster.com/auth/cli/sign-in?flow_id=1763c512-7aa8-4834-aa3f-3b35b0234909

  If you signed up, check your email to confirm your account.
  The CLI will automatically detect when you log in.

test@MSI:~/leverage-opus$ npx task-master init
  _____         _      __  __           _            
 |_   _|_ _ ___| | __ |  \/  | __ _ ___| |_ ___ _ __ 
   | |/ _` / __| |/ / | |\/| |/ _` / __| __/ _ \ '__|
   | | (_| \__ \   <  | |  | | (_| \__ \ ||  __/ |   
   |_|\__,_|___/_|\_\ |_|  |_|\__,_|___/\__\___|_|   
                                                     
by x.com/eyaltoledano
Taskmaster for teams: tryhamster.com

You need a plan before you execute.

✔ How do you want to build it?
 Solo (Taskmaster)
Initialize a Git repository in project root? ✓ Yes
Store tasks in Git (tasks.json and tasks/ directory)? ✓ Yes
Set up AI IDE rules for better integration? ✓ Yes

Taskmaster Project Settings:
──────────────────────────────────────────────────
  Storage:                         Local File Storage
  AI IDE rules:                    ✓ Yes
  Response language:               y
  Initialize Git repository:       ✓ Yes
  Store tasks in Git:              ✓ Yes
──────────────────────────────────────────────────

→ Created directory: /home/test/leverage-opus/.taskmaster
→ Created directory: /home/test/leverage-opus/.taskmaster/tasks
→ Created directory: /home/test/leverage-opus/.taskmaster/docs
→ Created directory: /home/test/leverage-opus/.taskmaster/reports
→ Created directory: /home/test/leverage-opus/.taskmaster/templates
✓ Created initial state file: /home/test/leverage-opus/.taskmaster/state.json
→ Default tag set to "master" for task organization
→ Created file: /home/test/leverage-opus/.env.example
→ Created file: /home/test/leverage-opus/.taskmaster/config.json
✓ Created /home/test/leverage-opus/.gitignore with full template
→ Created file: /home/test/leverage-opus/.taskmaster/templates/example_prd.txt
→ Created file: /home/test/leverage-opus/.taskmaster/templates/example_prd_rpg.txt
→ Initializing Git repository due to --git flag...
✓ Git repository initialized

╭──────────────────────────────────────────────────────────╮
│ Configuring Rule Profiles...                             │
╰──────────────────────────────────────────────────────────╯
→ Running interactive rules setup. Please select which rule profiles to include.
  _____         _      __  __           _            
 |_   _|_ _ ___| | __ |  \/  | __ _ ___| |_ ___ _ __ 
   | |/ _` / __| |/ / | |\/| |/ _` / __| __/ _ \ '__|
   | | (_| \__ \   <  | |  | | (_| \__ \ ||  __/ |   
   |_|\__,_|___/_|\_\ |_|  |_|\__,_|___/\__\___|_|   
                                                     
by x.com/eyaltoledano                                                                                                                                                                                v0.40.0
Taskmaster for teams: tryhamster.com


╭───────────────────────────────────────────────────────────────────────────────────────────╮
│                                                                                           │
│   Rule Profiles Setup                                                                     │
│                                                                                           │
│   Rule profiles help enforce best practices and conventions for Task Master.              │
│   Each profile provides coding guidelines tailored for specific AI coding environments.   │
│                                                                                           │
│   Available Profiles:                                                                     │
│   • Amp - Integration guide and MCP config                                                │
│   • Claude Code - Integration guide with Task Master slash commands                       │
│   • Cline - Rule profile                                                                  │
│   • Codex - Comprehensive Task Master integration guide                                   │
│   • Cursor - Rule profile and MCP config                                                  │
│   • Gemini - Integration guide and MCP config                                             │
│   • Kilo Code - Rule profile and MCP config                                               │
│   • Kiro - Rule profile and MCP config                                                    │
│   • OpenCode - Integration guide and MCP config                                           │
│   • Roo Code - Rule profile, MCP config, and agent modes                                  │
│   • Trae - Rule profile                                                                   │
│   • VS Code - Rule profile and MCP config                                                 │
│   • Windsurf - Rule profile and MCP config                                                │
│   • Zed - Integration guide and MCP config                                                │
│                                                                                           │
╰───────────────────────────────────────────────────────────────────────────────────────────╯

✔ Which rule profiles would you like to add to your project? Claude Code
Installing 1 selected profile(s)...
Processing profile 1/1: claude...
[INFO] [Claude] Commands and agents are now available via the Task Master plugin
[INFO] [Claude] Install with: /plugin marketplace add taskmaster
[INFO] [Claude] Then: /plugin install taskmaster@taskmaster
[INFO] [Claude] Added Task Master import to existing /home/test/leverage-opus/CLAUDE.md
[INFO] [Claude] Enabled deferred MCP loading in /home/test/.bashrc
[INFO] [Claude] Restart your terminal for changes to take effect
[INFO] Setting up MCP configuration at /home/test/leverage-opus/.mcp.json...
[SUCCESS] Created MCP configuration file at /home/test/leverage-opus/.mcp.json
[INFO] MCP server will use the installed task-master-ai package
[INFO] [Claude] Commands and agents are now available via the Task Master plugin
[INFO] [Claude] Install with: /plugin marketplace add taskmaster
[INFO] [Claude] Then: /plugin install taskmaster@taskmaster
[INFO] [Claude] Task Master import already present in /home/test/leverage-opus/CLAUDE.md
Summary for claude: Integration guide installed.

Completed installation of all 1 profile(s).
✓ Rule profiles configured.

╭──────────────────────────────────────────────────────────╮
│ Configuring AI Models...                                 │
╰──────────────────────────────────────────────────────────╯
→ Running interactive model setup. Please select your preferred AI models.
  _____         _      __  __           _            
 |_   _|_ _ ___| | __ |  \/  | __ _ ___| |_ ___ _ __ 
   | |/ _` / __| |/ / | |\/| |/ _` / __| __/ _ \ '__|
   | | (_| \__ \   <  | |  | | (_| \__ \ ||  __/ |   
   |_|\__,_|___/_|\_\ |_|  |_|\__,_|___/\__\___|_|   
                                                     
by x.com/eyaltoledano                                                                                                                                                                                v0.40.0
Taskmaster for teams: tryhamster.com

Starting interactive model setup...

🎯 Interactive Model Setup
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 Navigation tips:
   • Type to search and filter options
   • Use ↑↓ arrow keys to navigate results
   • Standard models are listed first, custom providers at bottom
   • Press Enter to select

✔ Select the main model for generation/updates: No change
✔ Select the research model: No change
✔ Select the fallback model (optional): Cancel
✓ AI Models configured.

   ╔══════════════════════════════════════════════════════════╗
   ║                                                          ║
   ║     ____                              _                  ║
   ║    / ___| _   _  ___ ___ ___  ___ ___| |                 ║
   ║    \___ \| | | |/ __/ __/ _ \/ __/ __| |                 ║
   ║     ___) | |_| | (_| (_|  __/\__ \__ \_|                 ║
   ║    |____/ \__,_|\___\___\___||___/___(_)                 ║
   ║                                                          ║
   ║   Project initialized successfully!                      ║
   ║                                                          ║
   ╚══════════════════════════════════════════════════════════╝

╭──────────────────────────────────────────────────────────╮
│                                                          │
│   Workflow                                               │
│                                                          │
│   Things you should do next:                             │
│                                                          │
│   1. Configure AI models and add API keys to `.env`      │
│   ├─ Models: Use task-master models commands             │
│   └─ Keys: Add provider API keys to .env (or             │
│   .cursor/mcp.json)                                      │
│   2. Discuss your idea with AI and create a PRD          │
│   ├─ Simple projects: Use example_prd.txt template       │
│   └─ Complex systems: Use example_prd_rpg.txt template   │
│   3. Parse your PRD to generate initial tasks            │
│   └─ CLI: task-master parse-prd                          │
│   .taskmaster/docs/prd.txt                               │
│   4. Analyze task complexity                             │
│   └─ CLI: task-master analyze-complexity --research      │
│   5. Expand tasks into subtasks                          │
│   └─ CLI: task-master expand --all --research            │
│   6. Start working on tasks                              │
│   └─ CLI: task-master next                               │
│   7. Ship it!                                            │
│                                                          │
│   * Run task-master --help to see all available          │
│   commands                                               │
│   * Run tm rules --setup to configure AI IDE rules for   │
│   better integration                                     │
│                                                          │
╰──────────────────────────────────────────────────────────╯
```