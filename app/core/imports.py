from flask import Flask, Blueprint, render_template, url_for, redirect, request, flash
from datetime import datetime
from sqlite3 import *
from datetime import date, datetime
from flask_login import UserMixin, login_user, logout_user, current_user, login_required

""""""
def validar_cpf(cpf):
    cpf = ''.join(filter(str.isdigit, cpf))  # remove pontos, traços etc.

    if len(cpf) != 11 or cpf == cpf[0] * 11:
        return False

    def calcular_digito(cpf_parcial):
        soma = sum(int(num) * peso for num, peso in zip(cpf_parcial, range(len(cpf_parcial)+1, 1, -1)))
        resto = (soma * 10) % 11
        return 0 if resto == 10 else resto

    digito1 = calcular_digito(cpf[:9])
    digito2 = calcular_digito(cpf[:9] + str(digito1))

    return cpf[-2:] == f"{digito1}{digito2}"
