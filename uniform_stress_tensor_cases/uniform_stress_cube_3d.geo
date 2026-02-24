// ==========================================================
// INTERNSHIP AT CTU IN PRAGUE 
// Input geometry for Flow123D - Elastic isotropic material
// Problem: Statically determinate supported cube 
// ==========================================================

// Taking a unit cube in the first octant
L = 1.0;   // Cube dimension 
lc = 0.35; // Mesh density parameter / discretization step

// Definition of cube points (vertices)
Point(1) = {0, 0, 0, lc};  
Point(2) = {L, 0, 0, lc};  
Point(3) = {L, L, 0, lc};
Point(4) = {0, L, 0, lc};  
Point(5) = {0, 0, L, lc};
Point(6) = {L, 0, L, lc};
Point(7) = {L, L, L, lc};
Point(8) = {0, L, L, lc};

// Definition of cube lines (edges)
Line(1) = {1, 2}; 
Line(2) = {2, 3}; 
Line(3) = {3, 4}; 
Line(4) = {4, 1};
Line(5) = {1, 5}; 
Line(6) = {2, 6}; 
Line(7) = {3, 7}; 
Line(8) = {4, 8};
Line(9) = {5, 6}; 
Line(10) = {6, 7}; 
Line(11) = {7, 8}; 
Line(12) = {8, 5};

// Definition of cube surfaces (faces)
Line Loop(13) = {1, 2, 3, 4};      Plane Surface(1) = {13}; // Bottom surface in the xy plane (z=0)
Line Loop(14) = {9, 10, 11, 12};   Plane Surface(2) = {14}; // Top surface in the xy plane (z=L)
Line Loop(15) = {1, 6, -9, -5};    Plane Surface(3) = {15}; // Front surface in the xz plane (y=0)
Line Loop(16) = {2, 7, -10, -6};   Plane Surface(4) = {16}; // Right surface in the yz plane (x=L)
Line Loop(17) = {3, 8, -11, -7};   Plane Surface(5) = {17}; // Back surface in the xz plane (y=L)
Line Loop(18) = {4, 5, -12, -8};   Plane Surface(6) = {18}; // Left surface in the yz plane (x=0)

// Cube volume
Surface Loop(1) = {1, 2, 3, 4, 5, 6};
Volume(1) = {1};

// Definition of Physical groups (Physical Volume, then Physical Surface, and finally Physical Point):
Physical Volume("rock") = {1};

Physical Surface(".surface_z_plus")  = {2}; 
Physical Surface(".surface_z_minus") = {1}; 
Physical Surface(".surface_x_plus")  = {4}; 
Physical Surface(".surface_x_minus") = {6}; 
Physical Surface(".surface_y_plus")  = {5}; 
Physical Surface(".surface_y_minus") = {3}; 

Physical Point(".fix_point_3_DOFs") = {1};
Physical Point(".fix_point_2_DOFs") = {2};
Physical Point(".fix_point_1_DOFs") = {4};