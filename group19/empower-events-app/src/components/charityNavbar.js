import React, { useContext } from 'react';
import { Link, NavLink, useNavigate } from 'react-router-dom';
import { Navbar, Nav, Container } from 'react-bootstrap';
import 'bootstrap/dist/css/bootstrap.min.css';
import { UserContext } from '../contexts/userContext';
import axios from 'axios';

const AppNavbar = () => {
  const navigate = useNavigate();


  const onLogout = async () => {
    try {
      const csrfToken = document.cookie
        .split('; ')
        .find(row => row.startsWith('csrftoken='))
        ?.split('=')[1];

      if (!csrfToken) {
        console.error('CSRF token not found');
        return;
      }

      await axios.post('http://localhost:8000/api/charity/logout/', {}, {
        headers: {
          'X-CSRFToken': csrfToken, // Include the CSRF token manually
        },
      });
      navigate('/'); // Redirect to login page after logout
    } catch (error) {
      console.error('Error logging out:', error);
    }
  };


  return (
    <Navbar bg="dark" variant="dark" expand="lg">
      <Container>
        <Navbar.Brand as={Link} to="/admin/portal">Empower Events Admin Dashboard</Navbar.Brand>
        <Navbar.Toggle aria-controls="basic-navbar-nav" />
        <Navbar.Collapse id="basic-navbar-nav">
          <Nav className="me-auto">
            <NavLink className="nav-link" to="/admin/add-event">Add Event</NavLink>
            <NavLink className="nav-link" to="/admin/events">View Event Feedback</NavLink>
            <NavLink className="nav-link" to="/admin/leader-votes">View Activity leader votes</NavLink>
          </Nav>
          <Nav className="ms-auto">
            <NavLink className="nav-link" to="#" onClick={onLogout}>Logout</NavLink>
          </Nav>
        </Navbar.Collapse>
      </Container>
    </Navbar>
  );
};

export default AppNavbar;
