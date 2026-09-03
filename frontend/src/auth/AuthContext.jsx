import {
  createContext,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import {
  AuthApiError,
  fetchCurrentUser,
  loginUser,
  registerUser,
} from "../api/authApi";
import {
  readAccessToken,
  removeAccessToken,
  storeAccessToken,
} from "./authStorage";

// eslint-disable-next-line react-refresh/only-export-components
export const AuthContext = createContext(null);

function AuthProvider({ children }) {
  const [initialToken] = useState(readAccessToken);
  const [token, setToken] = useState(initialToken);
  const [user, setUser] = useState(null);
  const [isLoading, setIsLoading] = useState(Boolean(initialToken));
  const requestVersionRef = useRef(0);

  const clearAuth = useCallback(() => {
    requestVersionRef.current += 1;
    removeAccessToken();
    setToken(null);
    setUser(null);
    setIsLoading(false);
  }, []);

  useEffect(() => {
    const storedToken = initialToken;

    if (!storedToken) {
      return undefined;
    }

    const controller = new AbortController();
    const requestVersion = requestVersionRef.current + 1;
    requestVersionRef.current = requestVersion;

    async function restoreUser() {
      try {
        const currentUser = await fetchCurrentUser(storedToken, {
          signal: controller.signal,
        });

        if (requestVersionRef.current === requestVersion) {
          setUser(currentUser);
        }
      } catch (error) {
        if (controller.signal.aborted) {
          return;
        }

        if (requestVersionRef.current === requestVersion) {
          setUser(null);

          if (error instanceof AuthApiError && error.status === 401) {
            removeAccessToken();
            setToken(null);
          }
        }
      } finally {
        if (
          !controller.signal.aborted &&
          requestVersionRef.current === requestVersion
        ) {
          setIsLoading(false);
        }
      }
    }

    restoreUser();

    return () => {
      controller.abort();
    };
  }, [initialToken]);

  const login = useCallback(async ({ email, password }) => {
    const requestVersion = requestVersionRef.current + 1;
    requestVersionRef.current = requestVersion;
    const tokenResponse = await loginUser({ email, password });
    const nextToken = tokenResponse?.access_token;

    if (!nextToken) {
      throw new AuthApiError("The server returned an invalid login response.");
    }

    storeAccessToken(nextToken);
    setToken(nextToken);

    try {
      const currentUser = await fetchCurrentUser(nextToken);

      if (requestVersionRef.current === requestVersion) {
        setUser(currentUser);
      }

      return currentUser;
    } catch (error) {
      if (requestVersionRef.current === requestVersion) {
        removeAccessToken();
        setToken(null);
        setUser(null);
      }

      throw error;
    }
  }, []);

  const register = useCallback(
    async ({ email, password, displayName }) => {
      await registerUser({ email, password, displayName });

      try {
        return await login({ email, password });
      } catch (error) {
        error.accountCreated = true;
        throw error;
      }
    },
    [login]
  );

  const value = useMemo(
    () => ({
      user,
      token,
      isAuthenticated: Boolean(user && token),
      isLoading,
      login,
      register,
      logout: clearAuth,
    }),
    [clearAuth, isLoading, login, register, token, user]
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export default AuthProvider;
