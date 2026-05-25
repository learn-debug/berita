let redirectFn: (() => void) | null = null;

export function setRedirectFn(fn: () => void) {
  redirectFn = fn;
}

export function redirectToLogin() {
  if (redirectFn) {
    redirectFn();
  } else {
    if (typeof window !== "undefined") {
      window.location.href = "/login";
    }
  }
}
