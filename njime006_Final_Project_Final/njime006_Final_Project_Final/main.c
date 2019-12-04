/*
 * njime006_Final_Project_Final.c
 *
 * Created: 12/4/2019 11:02:23 AM
 * Author : Noah Jimenez
 */ 

#define F_CPU 8000000UL
#include <avr/io.h>
#include <avr/interrupt.h>
#include <util/delay.h>


#define DDR_SPI DDRB

#define DD_SS 4
#define DD_MOSI 5
#define DD_MISO 6
#define DD_SCK 7

unsigned char SPI_received_data = 0;

void SPI_ServantInit(void) {
	DDR_SPI |= (1 << DD_MISO);
	DDR_SPI &= ~(1 << DD_MOSI) & ~(1 << DD_SS) & ~(1 << DD_SCK);
	SPCR |= (1 << SPE) | (1 << SPIE);
	SREG |= (0x80);
}

ISR(SPI_STC_vect) {
	SPI_received_data = SPDR;
}

void set_PWM(double frequency) {
	static double current_frequency; // Keeps track of the currently set frequency
	// Will only update the registers when the frequency changes, otherwise allows
	// music to play uninterrupted.
	if (frequency != current_frequency) {
		if (!frequency) { TCCR0B &= 0x08; } //stops timer/counter
		else { TCCR0B |= 0x03; } // resumes/continues timer/counter
		
		// prevents OCR3A from overflowing, using prescaler 64
		// 0.954 is smallest frequency that will not result in overflow
		if (frequency < 0.954) { OCR0A = 0xFFFF; }
		
		// prevents OCR0A from underflowing, using prescaler 64
		// 31250 is largest frequency that will not result in underflow
		else if (frequency > 31250) { OCR0A = 0x0000; }
		
		// set OCR3A based on desired frequency
		else { OCR0A = (short)(8000000 / (128 * frequency)) - 1; }

		TCNT0 = 0; // resets counter
		current_frequency = frequency; // Updates the current frequency
	}
}

void PWM_on() {
	TCCR0A = (1 << WGM02) | (1 << WGM00) | (1 << COM0A0);
	// COM3A0: Toggle PB3 on compare match between counter and OCR0A
	TCCR0B = (1 << WGM02) | (1 << CS01) | (1 << CS00);
	// WGM02: When counter (TCNT0) matches OCR0A, reset counter
	// CS01 & CS30: Set a prescaler of 64
	set_PWM(0);
}

void PWM_off() {
	TCCR0A = 0x00;
	TCCR0B = 0x00;
}

int main(void)
{
	DDRB = 0xFF; PORTB = 0x00;
	DDRA = 0x00; PORTA = 0xFF;
	SPI_ServantInit();
	PWM_on();
	set_PWM(950);
	unsigned char Value = 0;
	
	while (1)
	{
		Value = SPI_received_data;
		if(Value == 1)
		{
			set_PWM(520);
			_delay_ms(1000);
		}
		if(Value == 0)
		{
			set_PWM(990);
			_delay_ms(1000);
		}
	}
}