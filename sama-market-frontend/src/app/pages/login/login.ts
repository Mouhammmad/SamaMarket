import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { AuthService } from '../../services/auth';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule, RouterLink],
  templateUrl: './login.html',
  styleUrl: './login.css'
})
export class Login {
  username = '';
  password = '';
  erreur = '';
  chargement = false;

  constructor(private authService: AuthService, private router: Router) {}

  onSubmit() {
    this.erreur = '';
    this.chargement = true;

    this.authService.login(this.username, this.password).subscribe({
      next: (res) => {
        this.authService.saveToken(res.access);
        this.chargement = false;
        this.router.navigate(['/']);
      },
      error: (err) => {
        this.erreur = 'Identifiants incorrects. Vérifie ton username et mot de passe.';
        this.chargement = false;
      }
    });
  }
}