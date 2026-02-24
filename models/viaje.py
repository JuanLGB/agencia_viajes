from datetime import datetime


class Viaje:
    def __init__(
        self,
        cliente,
        tipo,
        destino,
        precio_total,
        porcentaje_ganancia,
        fecha_limite,
        fecha_inicio,
        fecha_fin
    ):
        self.cliente = cliente
        self.tipo = tipo
        self.destino = destino
        self.precio_total = precio_total
        self.porcentaje_ganancia = porcentaje_ganancia

        self.fecha_limite = datetime.strptime(fecha_limite, "%d/%m/%Y")
        self.fecha_inicio = datetime.strptime(fecha_inicio, "%d/%m/%Y")
        self.fecha_fin = datetime.strptime(fecha_fin, "%d/%m/%Y")

        self.pagos = []


    def calcular_ganancia(self):
        return self.precio_total * (self.porcentaje_ganancia / 100)

    def registrar_pago(self, monto):
        self.pagos.append(monto)

    def total_pagado(self):
        return sum(self.pagos)

    def saldo_pendiente(self):
        return self.precio_total - self.total_pagado()

    def dias_para_vencimiento(self):
        hoy = datetime.now()
        diferencia = self.fecha_limite - hoy
        return diferencia.days

    def estado_pago(self):
        dias = self.dias_para_vencimiento()

        if self.saldo_pendiente() <= 0:
            return "PAGADO"
        elif dias < 0:
            return "VENCIDO"
        elif dias <= 3:
            return "POR VENCER"
        else:
            return "EN TIEMPO"
