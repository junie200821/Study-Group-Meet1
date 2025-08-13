import React, { useState, useEffect, useCallback } from 'react';
import axios from 'axios';
import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Textarea } from './components/ui/textarea';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './components/ui/card';
import { Badge } from './components/ui/badge';
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle, DialogTrigger } from './components/ui/dialog';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './components/ui/tabs';
import { Calendar, Clock, Users, Plus, Search, TrendingUp, BookOpen, Hash } from 'lucide-react';
import './App.css';

const API_BASE_URL = process.env.REACT_APP_BACKEND_URL;

function App() {
  const [sessions, setSessions] = useState([]);
  const [trendingSessions, setTrendingSessions] = useState([]);
  const [currentUser, setCurrentUser] = useState(null);
  const [loading, setLoading] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedTag, setSelectedTag] = useState('');
  
  // Form states
  const [isCreateDialogOpen, setIsCreateDialogOpen] = useState(false);
  const [isLoginDialogOpen, setIsLoginDialogOpen] = useState(false);
  const [createForm, setCreateForm] = useState({
    title: '',
    description: '',
    date_time: '',
    tags: ''
  });
  const [loginForm, setLoginForm] = useState({
    username: ''
  });

  // Fetch sessions
  const fetchSessions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/sessions`);
      setSessions(response.data.sessions || []);
    } catch (error) {
      console.error('Error fetching sessions:', error);
    }
  }, []);

  // Fetch trending sessions
  const fetchTrendingSessions = useCallback(async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/sessions/trending`);
      setTrendingSessions(response.data.trending_sessions || []);
    } catch (error) {
      console.error('Error fetching trending sessions:', error);
    }
  }, []);

  // Initial load
  useEffect(() => {
    fetchSessions();
    fetchTrendingSessions();
    
    // Set up polling for real-time updates
    const interval = setInterval(() => {
      fetchSessions();
      fetchTrendingSessions();
    }, 10000); // Poll every 10 seconds

    return () => clearInterval(interval);
  }, [fetchSessions, fetchTrendingSessions]);

  // Handle login
  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginForm.username.trim()) return;

    setLoading(true);
    try {
      const response = await axios.post(`${API_BASE_URL}/api/auth/login`, {
        username: loginForm.username
      });
      setCurrentUser(response.data.user);
      setIsLoginDialogOpen(false);
      setLoginForm({ username: '' });
    } catch (error) {
      console.error('Login error:', error);
      alert('Login failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle create session
  const handleCreateSession = async (e) => {
    e.preventDefault();
    if (!createForm.title.trim() || !createForm.description.trim()) return;

    setLoading(true);
    try {
      const sessionData = {
        title: createForm.title,
        description: createForm.description,
        date_time: createForm.date_time || null,
        tags: createForm.tags ? createForm.tags.split(',').map(tag => tag.trim()) : []
      };

      const response = await axios.post(`${API_BASE_URL}/api/sessions`, sessionData);
      
      if (response.status === 200) {
        setCreateForm({ title: '', description: '', date_time: '', tags: '' });
        setIsCreateDialogOpen(false);
        fetchSessions();
        fetchTrendingSessions();
        alert('Session created successfully!');
      }
    } catch (error) {
      console.error('Error creating session:', error);
      alert('Failed to create session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle join session
  const handleJoinSession = async (sessionId) => {
    if (!currentUser) {
      setIsLoginDialogOpen(true);
      return;
    }

    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/sessions/${sessionId}/join?username=${currentUser.username}`);
      fetchSessions();
      fetchTrendingSessions();
    } catch (error) {
      console.error('Error joining session:', error);
      alert('Failed to join session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Handle leave session
  const handleLeaveSession = async (sessionId) => {
    if (!currentUser) return;

    setLoading(true);
    try {
      await axios.post(`${API_BASE_URL}/api/sessions/${sessionId}/leave?username=${currentUser.username}`);
      fetchSessions();
      fetchTrendingSessions();
    } catch (error) {
      console.error('Error leaving session:', error);
      alert('Failed to leave session. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // Filter sessions
  const filteredSessions = sessions.filter(session => {
    const matchesSearch = session.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         session.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesTag = !selectedTag || session.tags?.includes(selectedTag);
    return matchesSearch && matchesTag;
  });

  // Get all unique tags
  const allTags = [...new Set(sessions.flatMap(session => session.tags || []))];

  // Format date
  const formatDate = (dateString) => {
    if (!dateString) return null;
    return new Date(dateString).toLocaleDateString('en-US', {
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Check if user has joined session
  const hasJoinedSession = (session) => {
    return currentUser && session.participant_usernames?.includes(currentUser.username);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="header-content">
            <div className="logo">
              <BookOpen className="logo-icon" />
              <h1>StudyMeet</h1>
            </div>
            
            <div className="header-actions">
              {currentUser ? (
                <div className="user-info">
                  <span>Welcome, {currentUser.username}!</span>
                  <Button 
                    variant="outline" 
                    onClick={() => setCurrentUser(null)}
                    className="logout-btn"
                  >
                    Logout
                  </Button>
                </div>
              ) : (
                <Dialog open={isLoginDialogOpen} onOpenChange={setIsLoginDialogOpen}>
                  <DialogTrigger asChild>
                    <Button className="login-btn">Sign In</Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Welcome to StudyMeet</DialogTitle>
                      <DialogDescription>
                        Enter your username to join study sessions
                      </DialogDescription>
                    </DialogHeader>
                    <form onSubmit={handleLogin} className="login-form">
                      <Input
                        placeholder="Enter your username"
                        value={loginForm.username}
                        onChange={(e) => setLoginForm({ username: e.target.value })}
                        disabled={loading}
                      />
                      <Button type="submit" disabled={loading || !loginForm.username.trim()}>
                        {loading ? 'Signing In...' : 'Sign In'}
                      </Button>
                    </form>
                  </DialogContent>
                </Dialog>
              )}
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h2>Find Your Perfect Study Group</h2>
            <p>Join collaborative learning sessions, connect with peers, and achieve your academic goals together.</p>
            
            <div className="hero-actions">
              <Dialog open={isCreateDialogOpen} onOpenChange={setIsCreateDialogOpen}>
                <DialogTrigger asChild>
                  <Button size="lg" className="create-btn">
                    <Plus className="w-5 h-5 mr-2" />
                    Create Session
                  </Button>
                </DialogTrigger>
                <DialogContent className="max-w-md">
                  <DialogHeader>
                    <DialogTitle>Create Study Session</DialogTitle>
                    <DialogDescription>
                      Set up a new study group session for others to join
                    </DialogDescription>
                  </DialogHeader>
                  <form onSubmit={handleCreateSession} className="create-form">
                    <div className="form-group">
                      <Input
                        placeholder="Session Title"
                        value={createForm.title}
                        onChange={(e) => setCreateForm({ ...createForm, title: e.target.value })}
                        disabled={loading}
                      />
                    </div>
                    <div className="form-group">
                      <Textarea
                        placeholder="Description"
                        value={createForm.description}
                        onChange={(e) => setCreateForm({ ...createForm, description: e.target.value })}
                        disabled={loading}
                      />
                    </div>
                    <div className="form-group">
                      <Input
                        type="datetime-local"
                        value={createForm.date_time}
                        onChange={(e) => setCreateForm({ ...createForm, date_time: e.target.value })}
                        disabled={loading}
                      />
                    </div>
                    <div className="form-group">
                      <Input
                        placeholder="Tags (comma separated)"
                        value={createForm.tags}
                        onChange={(e) => setCreateForm({ ...createForm, tags: e.target.value })}
                        disabled={loading}
                      />
                    </div>
                    <Button 
                      type="submit" 
                      disabled={loading || !createForm.title.trim() || !createForm.description.trim()}
                      className="w-full"
                    >
                      {loading ? 'Creating...' : 'Create Session'}
                    </Button>
                  </form>
                </DialogContent>
              </Dialog>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <main className="main">
        <div className="container">
          {/* Search and Filter */}
          <div className="search-section">
            <div className="search-bar">
              <Search className="search-icon" />
              <Input
                placeholder="Search sessions..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
              />
            </div>
            
            {allTags.length > 0 && (
              <div className="tag-filters">
                <Button
                  variant={selectedTag === '' ? 'default' : 'outline'}
                  size="sm"
                  onClick={() => setSelectedTag('')}
                >
                  All
                </Button>
                {allTags.map(tag => (
                  <Button
                    key={tag}
                    variant={selectedTag === tag ? 'default' : 'outline'}
                    size="sm"
                    onClick={() => setSelectedTag(tag)}
                  >
                    <Hash className="w-3 h-3 mr-1" />
                    {tag}
                  </Button>
                ))}
              </div>
            )}
          </div>

          {/* Tabs */}
          <Tabs defaultValue="all" className="session-tabs">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="all">All Sessions</TabsTrigger>
              <TabsTrigger value="trending">
                <TrendingUp className="w-4 h-4 mr-2" />
                Trending
              </TabsTrigger>
            </TabsList>
            
            <TabsContent value="all" className="sessions-grid">
              {filteredSessions.length === 0 ? (
                <div className="empty-state">
                  <BookOpen className="empty-icon" />
                  <h3>No sessions found</h3>
                  <p>Be the first to create a study session!</p>
                </div>
              ) : (
                filteredSessions.map(session => (
                  <Card key={session.id} className="session-card">
                    <CardHeader>
                      <div className="card-header-content">
                        <CardTitle className="session-title">{session.title}</CardTitle>
                        <div className="participant-count">
                          <Users className="w-4 h-4" />
                          <span>{session.participant_usernames?.length || 0}</span>
                        </div>
                      </div>
                      <CardDescription className="session-description">
                        {session.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="session-meta">
                        {session.date_time && (
                          <div className="session-date">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(session.date_time)}</span>
                          </div>
                        )}
                        
                        {session.tags && session.tags.length > 0 && (
                          <div className="session-tags">
                            {session.tags.map(tag => (
                              <Badge key={tag} variant="secondary" className="tag">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      
                      <div className="session-actions">
                        {hasJoinedSession(session) ? (
                          <Button 
                            variant="outline" 
                            onClick={() => handleLeaveSession(session.id)}
                            disabled={loading}
                            className="leave-btn"
                          >
                            Leave Session
                          </Button>
                        ) : (
                          <Button 
                            onClick={() => handleJoinSession(session.id)}
                            disabled={loading}
                            className="join-btn"
                          >
                            Join Session
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>
            
            <TabsContent value="trending" className="sessions-grid">
              {trendingSessions.length === 0 ? (
                <div className="empty-state">
                  <TrendingUp className="empty-icon" />
                  <h3>No trending sessions</h3>
                  <p>Popular sessions will appear here</p>
                </div>
              ) : (
                trendingSessions.map(session => (
                  <Card key={session.id} className="session-card trending">
                    <CardHeader>
                      <div className="card-header-content">
                        <CardTitle className="session-title">{session.title}</CardTitle>
                        <div className="participant-count trending">
                          <Users className="w-4 h-4" />
                          <span>{session.participant_usernames?.length || 0}</span>
                          <TrendingUp className="w-4 h-4 trending-icon" />
                        </div>
                      </div>
                      <CardDescription className="session-description">
                        {session.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="session-meta">
                        {session.date_time && (
                          <div className="session-date">
                            <Calendar className="w-4 h-4" />
                            <span>{formatDate(session.date_time)}</span>
                          </div>
                        )}
                        
                        {session.tags && session.tags.length > 0 && (
                          <div className="session-tags">
                            {session.tags.map(tag => (
                              <Badge key={tag} variant="secondary" className="tag">
                                {tag}
                              </Badge>
                            ))}
                          </div>
                        )}
                      </div>
                      
                      <div className="session-actions">
                        {hasJoinedSession(session) ? (
                          <Button 
                            variant="outline" 
                            onClick={() => handleLeaveSession(session.id)}
                            disabled={loading}
                            className="leave-btn"
                          >
                            Leave Session
                          </Button>
                        ) : (
                          <Button 
                            onClick={() => handleJoinSession(session.id)}
                            disabled={loading}
                            className="join-btn"
                          >
                            Join Session
                          </Button>
                        )}
                      </div>
                    </CardContent>
                  </Card>
                ))
              )}
            </TabsContent>
          </Tabs>
        </div>
      </main>
    </div>
  );
}

export default App;