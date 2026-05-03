// Mobile App - Main Entry Point

import React from 'react'
import { NavigationContainer } from '@react-navigation/native'
import { createNativeStackNavigator } from '@react-navigation/stack'
import { createBottomTabNavigator } from '@react-navigation/bottom-tabs'
import { SafeAreaProvider } from 'react-native-safe-area-context'
import { GestureHandlerRootView } from 'react-native-gesture-handler'
import Icon from 'react-native-vector-icons/MaterialCommunityIcons'
import Toast from 'react-native-toast-message'

// Screens
import LoginScreen from './screens/auth/LoginScreen'
import SignupScreen from './screens/auth/SignupScreen'
import DashboardScreen from './screens/dashboard/DashboardScreen'
import CoursesScreen from './screens/courses/CoursesScreen'
import CourseDetailScreen from './screens/courses/CourseDetailScreen'
import LoansScreen from './screens/loans/LoansScreen'
import LoanCalculatorScreen from './screens/loans/LoanCalculatorScreen'
import ChatScreen from './screens/chat/ChatScreen'
import ProfileScreen from './screens/profile/ProfileScreen'
import SplashScreen from './screens/auth/SplashScreen'

const Stack = createNativeStackNavigator()
const Tab = createBottomTabNavigator()

// ============================================================================
// AUTH STACK
// ============================================================================

function AuthStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: false,
        animationEnabled: true,
      }}
    >
      <Stack.Screen name="Splash" component={SplashScreen} />
      <Stack.Screen name="Login" component={LoginScreen} />
      <Stack.Screen name="Signup" component={SignupScreen} />
    </Stack.Navigator>
  )
}

// ============================================================================
// APP STACK (BOTTOM TAB NAVIGATION)
// ============================================================================

function DashboardStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: '#111827' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="DashboardHome"
        component={DashboardScreen}
        options={{ title: 'Dashboard' }}
      />
    </Stack.Navigator>
  )
}

function CoursesStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: '#111827' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="CoursesList"
        component={CoursesScreen}
        options={{ title: 'Explore Courses' }}
      />
      <Stack.Screen
        name="CourseDetail"
        component={CourseDetailScreen}
        options={{ title: 'Course Details' }}
      />
    </Stack.Navigator>
  )
}

function LoansStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: '#111827' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="LoansList"
        component={LoansScreen}
        options={{ title: 'Loans' }}
      />
      <Stack.Screen
        name="LoanCalculator"
        component={LoanCalculatorScreen}
        options={{ title: 'EMI Calculator' }}
      />
    </Stack.Navigator>
  )
}

function ChatStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: '#111827' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="ChatHome"
        component={ChatScreen}
        options={{ title: 'AI Assistant' }}
      />
    </Stack.Navigator>
  )
}

function ProfileStack() {
  return (
    <Stack.Navigator
      screenOptions={{
        headerShown: true,
        headerStyle: { backgroundColor: '#111827' },
        headerTintColor: '#fff',
        headerTitleStyle: { fontWeight: 'bold' },
      }}
    >
      <Stack.Screen
        name="ProfileHome"
        component={ProfileScreen}
        options={{ title: 'Profile' }}
      />
    </Stack.Navigator>
  )
}

function AppStack() {
  return (
    <Tab.Navigator
      screenOptions={({ route }) => ({
        headerShown: false,
        tabBarIcon: ({ focused, color, size }) => {
          let iconName = ''

          if (route.name === 'Dashboard') {
            iconName = focused ? 'home' : 'home-outline'
          } else if (route.name === 'Courses') {
            iconName = focused ? 'book' : 'book-outline'
          } else if (route.name === 'Loans') {
            iconName = focused ? 'cash-multiple' : 'cash-multiple'
          } else if (route.name === 'Chat') {
            iconName = focused ? 'chat' : 'chat-outline'
          } else if (route.name === 'Profile') {
            iconName = focused ? 'account' : 'account-outline'
          }

          return <Icon name={iconName} size={size} color={color} />
        },
        tabBarActiveTintColor: '#0ea5e9',
        tabBarInactiveTintColor: '#6b7280',
        tabBarStyle: {
          backgroundColor: '#fff',
          borderTopColor: '#e5e7eb',
          borderTopWidth: 1,
          paddingBottom: 5,
        },
      })}
    >
      <Tab.Screen
        name="Dashboard"
        component={DashboardStack}
        options={{ title: 'Home' }}
      />
      <Tab.Screen
        name="Courses"
        component={CoursesStack}
        options={{ title: 'Courses' }}
      />
      <Tab.Screen
        name="Loans"
        component={LoansStack}
        options={{ title: 'Loans' }}
      />
      <Tab.Screen
        name="Chat"
        component={ChatStack}
        options={{ title: 'Chat' }}
      />
      <Tab.Screen
        name="Profile"
        component={ProfileStack}
        options={{ title: 'Profile' }}
      />
    </Tab.Navigator>
  )
}

// ============================================================================
// MAIN APP
// ============================================================================

export default function App() {
  const [isSignedIn, setIsSignedIn] = React.useState(false)
  const [isLoading, setIsLoading] = React.useState(true)

  // Check if user is logged in on app start
  React.useEffect(() => {
    const checkAuth = async () => {
      try {
        // In real app, check AsyncStorage for auth token
        const token = null // await AsyncStorage.getItem('authToken')
        setIsSignedIn(!!token)
      } catch (error) {
        console.error('Auth check error:', error)
      } finally {
        setIsLoading(false)
      }
    }

    checkAuth()
  }, [])

  if (isLoading) {
    return null // Show splash screen here
  }

  return (
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <NavigationContainer>
          {isSignedIn ? <AppStack /> : <AuthStack />}
        </NavigationContainer>
        <Toast />
      </SafeAreaProvider>
    </GestureHandlerRootView>
  )
}
