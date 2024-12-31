

// 🖥️ my year in javascript
setInterval(() => {
    const tasks = ["Coffee", "Procrastinate", "Fix bugs", "Create more bugs"];
    const emotions = ["😅", "🤯", "💡", "😭"];
    console.log(`Doing: ${tasks[Math.random() * tasks.length | 0]} ${emotions[Math.random() * emotions.length | 0]}`);
  }, 2000);
  
  console.log("👨‍💻 Starting life logs...");
