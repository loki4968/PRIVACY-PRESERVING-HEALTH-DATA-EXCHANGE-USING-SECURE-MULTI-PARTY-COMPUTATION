import React from 'react';
import { Navbar, Nav, Container, NavDropdown } from 'react-bootstrap';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

const Navigation = () => {
  const { currentUser, logout } = useAuth();
  const location = useLocation();
  
  return (
    <Navbar bg="dark" variant="dark" expand="lg" className="mb-4">
      <Container>
        <Navbar.Brand as={Link} to="/dashboard">Health Data Exchange</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <Nav.Link 
              as={Link} 
              to="/dashboard" 
              active={location.pathname === '/dashboard'}
            >
              Dashboard
            </Nav.Link>
            
            <Nav.Link 
              as={Link} 
              to="/health-data" 
              active={location.pathname === '/health-data'}
            >
              Health Data
            </Nav.Link>
            
            <Nav.Link 
              as={Link} 
              to="/secure-computation" 
              active={location.pathname === '/secure-computation'}
            >
              Secure Computation
            </Nav.Link>
            
            <Nav.Link 
              as={Link} 
              to="/report-requests" 
              active={location.pathname === '/report-requests'}
            >
              Report Requests
            </Nav.Link>
            
            <NavDropdown 
              title="Machine Learning" 
              id="ml-nav-dropdown"
              active={['/ml-dashboard', '/federated-learning', '/risk-assessment', '/time-series', '/report-requests'].includes(location.pathname)}
            >
              <NavDropdown.Item 
                as={Link} 
                to="/ml-dashboard"
                active={location.pathname === '/ml-dashboard'}
              >
                ML Dashboard
              </NavDropdown.Item>
              <NavDropdown.Item 
                as={Link} 
                to="/federated-learning"
                active={location.pathname === '/federated-learning'}
              >
                Federated Learning
              </NavDropdown.Item>
              <NavDropdown.Item 
                as={Link} 
                to="/risk-assessment"
                active={location.pathname === '/risk-assessment'}
              >
                Risk Assessment
              </NavDropdown.Item>
              <NavDropdown.Item 
                as={Link} 
                to="/time-series"
                active={location.pathname === '/time-series'}
              >
                Time Series Analysis
              </NavDropdown.Item>
            </NavDropdown>
          </Nav>
          
          <Nav>
            {currentUser ? (
              <>
                <Nav.Link 
                  as={Link} 
                  to="/profile" 
                  active={location.pathname === '/profile'}
                >
                  Profile
                </Nav.Link>
                <Nav.Link onClick={logout}>Logout</Nav.Link>
              </>
            ) : (
              <>
                <Nav.Link 
                  as={Link} 
                  to="/login" 
                  active={location.pathname === '/login'}
                >
                  Login
                </Nav.Link>
                <Nav.Link 
                  as={Link} 
                  to="/register" 
                  active={location.pathname === '/register'}
                >
                  Register
                </Nav.Link>
              </>
            )}
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default Navigation;