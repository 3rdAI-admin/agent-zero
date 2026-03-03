// Inline button two-click confirmation for destructive actions.
// First click arms, second click confirms, timeout resets.

const CONFIRM_TIMEOUT = 2000;
const CONFIRM_CLASS = 'confirming';
const CONFIRM_ICON = 'check';
const CONFIRM_TEXT = 'Confirm';

const buttonStates = new WeakMap();

// Handles inline two-click confirmation for a button.
export function confirmClick(event, action) {
  const button = event.currentTarget;
  if (!button) return;

  const state = buttonStates.get(button);

  if (state?.confirming) {
    clearTimeout(state.timeoutId);
    resetButton(button, state);
    buttonStates.delete(button);
    action();
  } else {
    const iconEl = button.querySelector('.material-symbols-outlined, .material-icons-outlined');
    const isIconButton = iconEl && button.textContent.trim() === iconEl.textContent.trim();
    
    const newState = {
      confirming: true,
      isIconButton,
      originalIcon: iconEl?.textContent?.trim(),
      originalHTML: isIconButton ? null : button.innerHTML,
      timeoutId: setTimeout(() => {
        resetButton(button, newState);
        buttonStates.delete(button);
      }, CONFIRM_TIMEOUT)
    };
    
    buttonStates.set(button, newState);
    button.classList.add(CONFIRM_CLASS);
    
    if (isIconButton && iconEl) {
      // Icon-only button: just swap icon
      iconEl.textContent = CONFIRM_ICON;
    } else {
      // Text button: show icon + optional "Confirm" text
      const originalText = button.textContent.trim();
      const confirmContent = originalText.length >= 4
        ? `<span class="material-symbols-outlined">${CONFIRM_ICON}</span>${CONFIRM_TEXT}`
        : `<span class="material-symbols-outlined">${CONFIRM_ICON}</span>`;
      button.innerHTML = confirmContent;
    }
  }
}

// Reset button to original state
function resetButton(button, state) {
  button.classList.remove(CONFIRM_CLASS);
  if (state.isIconButton) {
    const iconEl = button.querySelector('.material-symbols-outlined, .material-icons-outlined');
    if (iconEl && state.originalIcon) {
      iconEl.textContent = state.originalIcon;
    }
  } else if (state.originalHTML) {
    button.innerHTML = state.originalHTML;
  }
}

// Register Alpine magic helper.
// Uses alpine:init event so the magic is available before Alpine processes
// components, avoiding a race where queueMicrotask(start) fires before the
// caller can invoke registerAlpineMagic().
export function registerAlpineMagic() {
  const register = () => Alpine.magic('confirmClick', () => confirmClick);

  if (globalThis.Alpine) {
    // Alpine already loaded — register immediately (works for late-init components)
    register();
  }

  // Also hook the alpine:init event which fires *during* Alpine.start() but
  // before any component is initialized — guarantees the magic is present.
  document.addEventListener('alpine:init', () => {
    if (globalThis.Alpine) {
      register();
    }
  });
}

