import * as initializer from "./initializer.js";
import * as _modals from "./modals.js";
import * as _components from "./components.js";
import { registerAlpineMagic } from "./confirmClick.js";

// initialize required elements
await initializer.initialize();

// Register all Alpine extensions (magics + directives) via alpine:init.
// This event fires during Alpine.start() but BEFORE any component is
// initialized, avoiding the race where queueMicrotask(start) fires
// before we can call Alpine.magic() / Alpine.directive().
registerAlpineMagic();

document.addEventListener("alpine:init", () => {
  // add x-destroy directive to alpine
  Alpine.directive(
    "destroy",
    (_el, { expression }, { evaluateLater, cleanup }) => {
      const onDestroy = evaluateLater(expression);
      cleanup(() => onDestroy());
    }
  );

  // add x-create directive to alpine
  Alpine.directive(
    "create",
    (_el, { expression }, { evaluateLater }) => {
      const onCreate = evaluateLater(expression);
      onCreate();
    }
  );

  // run every second if the component is active
  Alpine.directive(
    "every-second",
    (_el, { expression }, { evaluateLater, cleanup }) => {
      const onTick = evaluateLater(expression);
      const intervalId = setInterval(() => onTick(), 1000);
      cleanup(() => clearInterval(intervalId));
    }
  );

  // run every minute if the component is active
  Alpine.directive(
    "every-minute",
    (_el, { expression }, { evaluateLater, cleanup }) => {
      const onTick = evaluateLater(expression);
      const intervalId = setInterval(() => onTick(), 60_000);
      cleanup(() => clearInterval(intervalId));
    }
  );

  // run every hour if the component is active
  Alpine.directive(
    "every-hour",
    (_el, { expression }, { evaluateLater, cleanup }) => {
      const onTick = evaluateLater(expression);
      const intervalId = setInterval(() => onTick(), 3_600_000);
      cleanup(() => clearInterval(intervalId));
    }
  );
});

// import alpine library (auto-starts via queueMicrotask)
await import("../vendor/alpine/alpine.min.js");
