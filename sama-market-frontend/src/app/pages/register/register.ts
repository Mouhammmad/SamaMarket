import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './register.html',
  styleUrl: './register.css'
})
export class Register {
  prenom = '';
  nom = '';
  email = '';
  phone = '';
  password = '';
  confirmation = '';
  role = 'CUSTOMER';
  erreur = '';
  chargement = false;

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit() {
    this.erreur = '';

    if (this.password !== this.confirmation) {
      this.erreur = 'Les mots de passe ne correspondent pas.';
      return;
    }

    this.chargement = true;

    const data = {
      username: (this.prenom + this.nom).toLowerCase().replace(/\s/g, ''),
      first_name: this.prenom,
      last_name: this.nom,
      email: this.email,
      phone: this.phone,
      password: this.password,
      role: this.role
    };

    this.authService.register(data).subscribe({
      next: () => {
        this.chargement = false;
        this.router.navigate(['/login']);
      },
      error: (err) => {
        this.erreur = 'Erreur lors de la création du compte. Vérifie les champs.';
        this.chargement = false;
      }
    });
  }
}